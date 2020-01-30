from openvino.inference_engine import IENetwork, IECore
import time
import os
import cv2
import infer_async

workspace_dir = os.path.join(os.environ['HOME'], 'object_detection_ncs2')
test_image = cv2.imread(os.path.join(workspace_dir, 'benchmark/car.png'))
models_dir = os.path.join(workspace_dir, 'benchmark/models')

iterations = 50


print('select model')
model = {}
for i, m in enumerate(os.listdir(models_dir)):
    model[i+1] = m
    print(i+1, m)

model_ind = int(input())
print(model[model_ind], ' selected')

model_xml = os.path.join(
    models_dir, model[model_ind], 'frozen_inference_graph.xml')
model_bin = os.path.join(
    models_dir, model[model_ind], 'frozen_inference_graph.bin')

assert os.path.isfile(model_bin)
assert os.path.isfile(model_xml)


print('select infer requests')
infer_req = int(input())

ie = IECore()
net = IENetwork(model=model_xml, weights=model_bin)

if infer_req == 1:

    print('starting sync with 1 requests')

    t0 = time.time()
    exec_net = ie.load_network(
        network=net, num_requests=2, device_name='MYRIAD')
    t1 = time.time()

    print(model[model_ind], str(round((t1 - t0), 4)), 'sec')

    input_blob = None
    feed_dict = {}
    for blob_name in net.inputs:
        if len(net.inputs[blob_name].shape) == 4:
            input_blob = blob_name
    output_blop = next(iter(net.outputs))
    n, c, h, w = net.inputs[input_blob].shape

    infered_images = 0
    t_start = time.time()
    for i in range(iterations):

        # preprocess image
        image = cv2.resize(test_image, (w, h))  # h w c
        image = image.transpose((2, 0, 1))  # c h w
        image = image.reshape(n, c, h, w)  # n c h w
        feed_dict[input_blob] = image
        exec_net.start_async(request_id=0, inputs=feed_dict)

        if exec_net.requests[0].wait(-1) == 0:
            res = exec_net.requests[0].outputs[output_blop]
            infered_images += 1
            fps = str(infered_images / (time.time() - t_start))
            print('FPS: ', fps,
                  end='\r', flush=True)

    print(fps)

else:

    print('starting async with ', str(infer_req), ' requests')

    exec_model = infer_async.InferenceModel().create_exec_infer_model(
        ie, net, model_xml, model_bin, infer_req)

    test_images = [test_image] * iterations

    infered_images = 0
    t_start = time.time()
    while True:
        results = exec_model.infer_frames(test_images)
        for res in results:
            infered_images += 1
            fps = str(infered_images / (time.time() - t_start))
            print('FPS: ', fps, end='\r', flush=True)

        if not test_images:
            break
    print(fps)
