from openvino.inference_engine import IENetwork, IECore
import time
import os
import cv2
import infer_async

workspace_dir = os.path.join(os.environ['HOME'], 'object_detection_ncs2')
test_image = cv2.imread(os.path.join(workspace_dir, 'benchmark/car.png'))

iterations = 100


for model in os.listdir(os.path.join(workspace_dir, 'benchmark/models')):

    model_xml = os.path.join(
        workspace_dir, 'benchmark/models', model, 'frozen_inference_graph.xml')
    model_bin = os.path.join(
        workspace_dir, 'benchmark/models', model, 'frozen_inference_graph.bin')

    assert os.path.isfile(model_bin)
    assert os.path.isfile(model_xml)

    ie = IECore()
    net = IENetwork(model=model_xml, weights=model_bin)

    for infer_req in range(1, 5):

        if infer_req == 1:

            # Syncron

            exec_net = ie.load_network(
                network=net, num_requests=1, device_name='MYRIAD')

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
                    print(model + ', infer req ' + str(infer_req) +
                          ': Fps ' + fps, end='\r', flush=True)
            del exec_net
        else:

            # Asynron

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
                    print(model + ', infer req ' + str(infer_req) +
                          ': Fps ' + fps, end='\r', flush=True)

                if not test_images:
                    break
            del exec_model
        print(model + ', infer req ' +
              str(infer_req) + ': Fps ' + fps)

    del ie
    del net
