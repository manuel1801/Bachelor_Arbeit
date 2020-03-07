from openvino.inference_engine import IENetwork, IECore
import time
import os
import cv2
import infer_async

models_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit', 'openvino_models')

test_image = cv2.imread(os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit', 'Inference_Engine_Tools/benchmark_tool/car.png'))


iterations = 100

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
exported_model = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'exported_model')

print('select infer requests (0 für synchron)')
infer_req = int(input())

ie = IECore()
net = IENetwork(model=model_xml, weights=model_bin)


if infer_req == 0:

    # Synchron
    if os.path.isfile(exported_model):  # found exported mode
        print('found model to import')
        exec_net = ie.import_network(
            model_file=exported_model, device_name='MYRIAD',
            num_requests=1)
    else:
        print('creating exec model')
        exec_net = ie.load_network(
            network=net, num_requests=1, device_name='MYRIAD')
        exec_net.export(exported_model)

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

    exec_model = infer_async.InferenceModel().create_exec_infer_model(
        ie, net, model_xml, model_bin, exported_model, infer_req)

    test_images = [test_image] * iterations

    infered_images = 0
    t_start = time.time()
    while True:
        results = exec_model.infer_frames(test_images)
        for res in results:
            infered_images += 1
            fps = str(infered_images / (time.time() - t_start))
            print('FPS: ', fps, end='\r', flush=True)

        if infered_images == iterations:
            break
    print(fps)
