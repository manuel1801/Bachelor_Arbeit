from openvino.inference_engine import IENetwork, IECore
import time
import os
import cv2
import infer_async

workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit')
test_image = cv2.imread(os.path.join(
    workspace_dir, 'Inference_Engine_Tools/benchmark_tool/car.png'))
models_dir = os.path.join(workspace_dir, 'openvino_models')

iterations = 200


print('select model')
selected_model = {}
i = 1
for dataset in os.listdir(models_dir):
    dataset_dir = os.path.join(models_dir, dataset)
    if os.path.isdir(dataset_dir):
        for model in os.listdir(dataset_dir):
            model_dir = os.path.join(dataset_dir, model)
            if os.path.isdir(model_dir):
                selected_model[i] = dataset, model
                print(i, dataset, model)
                i += 1


model_ind = int(input())
print(selected_model[model_ind], ' selected')

model_xml = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.xml')
model_bin = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.bin')

assert os.path.isfile(model_bin)
assert os.path.isfile(model_xml)


print('select infer requests (0 für synchron)')
infer_req = int(input())

ie = IECore()
net = IENetwork(model=model_xml, weights=model_bin)

fps_all = {}

if infer_req == 0:

    print('starting sync with 1 requests')

    t0 = time.time()
    exec_net = ie.load_network(
        network=net, num_requests=2, device_name='MYRIAD')
    t1 = time.time()

    print(selected_model[model_ind], str(round((t1 - t0), 4)), 'sec')

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

        if (i+1) % 50 == 0:
            print('saving: ')
            fps_all[i+1] = fps_current

        if exec_net.requests[0].wait(-1) == 0:
            res = exec_net.requests[0].outputs[output_blop]
            infered_images += 1
            fps_current = str(infered_images / (time.time() - t_start))
            print('FPS: ', fps_current,
                  end='\r', flush=True)

    for it, fps in fps_all.items():
        print('At iter: ', it, ' FPS: ', fps)


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
            fps_current = str(infered_images / (time.time() - t_start))
            print('FPS: ', fps_current, end='\r', flush=True)
        if (infered_images + 1) % 50 == 0:
            fps_all[infered_images + 1] = fps_current
        if infered_images == iterations:
            break
    for it, fps in fps_all.items():
        print('At iter: ', it, ' FPS: ', fps)
