#!/usr/bin/env python3

import cv2
import os
import sys
import time

import numpy as np
from openvino.inference_engine import IENetwork, IEPlugin

from multiprocessing import Process, Queue
import multiprocessing
import threading
import queue

# Sample from: https://github.com/decemberpei/openvino-ncs2-python-samples


def async_infer_worker(exe_net, request_number, image_queue, input_blob, out_blob):
    global start_time

    current_request_ids = range(request_number)
    next_request_ids = range(request_number, request_number * 2)
    done = False
    last_batch = -1
    infered_images = 0
    while True:
        buffers = []
        for i in range(request_number):
            b = image_queue.get()
            if type(b) != np.ndarray:
                buffers.append(None)
                done = True
                break
            else:
                buffers.append(b)
        for _request_id in current_request_ids:
            if _request_id >= request_number:
                if type(buffers[_request_id - request_number]) == np.ndarray:
                    exe_net.start_async(request_id=_request_id, inputs={
                                        input_blob: buffers[_request_id - request_number]})
                else:
                    #print("image at index " + str(_request_id - request_number) + " is none." )
                    last_batch = _request_id - request_number
                    break
            else:
                if type(buffers[_request_id]) == np.ndarray:
                    exe_net.start_async(request_id=_request_id, inputs={
                                        input_blob: buffers[_request_id]})
                else:
                    #print("image at index " + str(_request_id) + " is none." )
                    last_batch = _request_id
                    break

        for _request_id in next_request_ids:
            if exe_net.requests[_request_id].wait(-1) == 0:
                res = exe_net.requests[_request_id].outputs[out_blob]
                infered_images = infered_images + 1
                #print("infer result: label:%f confidence:%f left:%f top:%f right:%f bottom:%f" %(res[0][0][0][1], res[0][0][0][2], res[0][0][0][3], res[0][0][0][4], res[0][0][0][5], res[0][0][0][6]))
                duration = time.time() - start_time
                print("inferred images: " + str(infered_images) + ", average fps: " +
                      str(infered_images/duration) + "\r", end='', flush=False)

        current_request_ids, next_request_ids = next_request_ids, current_request_ids

        # for i in range(len(buffers)):
        #    image_queue.task_done()

        if done:
            break

    # 'last_batch' more inference results remain to check
    buffer_index = 0
    for _request_id in next_request_ids:
        if(buffer_index >= last_batch):
            break
        buffer_index = buffer_index + 1
        if exe_net.requests[_request_id].wait(-1) == 0:
            res = exe_net.requests[_request_id].outputs[out_blob]
            infered_images = infered_images + 1
            #print("infer result: label:%f confidence:%f left:%f top:%f right:%f bottom:%f" %(res[0][0][0][1], res[0][0][0][2], res[0][0][0][3], res[0][0][0][4], res[0][0][0][5], res[0][0][0][6]))
            duration = time.time() - start_time
            print("inferred images: " + str(infered_images) + ", average fps: " +
                  str(infered_images/duration) + "\r", end='', flush=False)


# for test purpose only
image_number = 300


def preprocess_worker(image_queue, n, c, h, w):
    test_images_dir = '/home/manuel/Bachelor_Arbeit/workspace/OI_Animals_9/validation/'
    images = [
        os.path.join(test_images_dir, img) for img in os.listdir(test_images_dir) if img[-3:] == 'jpg']
    for img_path in images:
        image = cv2.imread(img_path)
        image = cv2.resize(image, (w, h))
        image = image.transpose((2, 0, 1))
        image = image.reshape((n, c, h, w))
        image_queue.put(image)
    image_queue.put(None)


start_time = -1

# ./async_api_multi-processes_multi-requests.py <request number>


def main():
    global start_time

    # specify simutaneous request number in argv
    request_number = 3

    image_queue = multiprocessing.Queue(maxsize=request_number*3)

    model = {1: ['Samples', 'ssd_mobilenet_v2'],
             2: ['Samples', 'ssd_inception_v2'],
             3: ['Samples', 'faster_rcnn_inception_v2'],
             4: ['Samples', 'faster_rcnn_inception_v2_gray'],
             5: ['Animals', 'ssd_inception_v2'],
             6: ['Animals', 'faster_rcnn_inception_v2'],
             7: ['Animals', 'faster_rcnn_inception_v2_gray'],
             8: ['Animals', 'ssd_mobilenet_oi'],
             9: ['coco', 'ssd_fpn_resnet50']}

    model_ind = 6

    workspace_dir = os.path.join(os.environ['HOME'], 'object_detection_ncs2')
    model_xml = os.path.join(
        workspace_dir, 'models', model[model_ind][0], model[model_ind][1], 'frozen_inference_graph.xml')
    model_bin = os.path.join(
        workspace_dir, 'models', model[model_ind][0], model[model_ind][1], 'frozen_inference_graph.bin')

    plugin = IEPlugin(device="MYRIAD")
    net = IENetwork(model=model_xml, weights=model_bin)
    #input_blob = next(iter(net.inputs))
    for blob_name in net.inputs:
        if len(net.inputs[blob_name].shape) == 4:
            input_blob = blob_name

    out_blob = next(iter(net.outputs))
    n, c, h, w = net.inputs[input_blob].shape
    exec_net = plugin.load(network=net, num_requests=request_number*2)

    start_time = time.time()

    preprocess_thread = None
    preprocess_thread = threading.Thread(
        target=preprocess_worker, args=(image_queue, n, c, h, w))
    preprocess_thread.start()

    async_infer_worker(exec_net, request_number,
                       image_queue, input_blob, out_blob)

    preprocess_thread.join()

    print()

    del exec_net
    del net
    del plugin


if __name__ == '__main__':
    sys.exit(main() or 0)
