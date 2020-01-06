
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser, SUPPRESS
import cv2
import time
import logging as log
import pyrealsense2 as rs
import numpy as np
import datetime
from random import shuffle

# hier noch neue Socket connectin (non blocking) implementieren!!

from openvino.inference_engine import IENetwork, IECore

workspace_dir = '/home/manuel/Bachelor_Arbeit/workspace'
dataset = 'OI_Animals_Augmented_9_2000'
model = 'faster_rcnn_inception_v2_coco_2018_01_28_out'

# test_images_dir = '/home/manuel/Bachelor_Arbeit/test'


class Animal_Detection:
    def __init__(self):


def main():
    log.basicConfig(format="[ %(levelname)s ] %(message)s",
                    level=log.INFO, stream=sys.stdout)

    model_xml = os.path.join(workspace_dir, dataset, model,
                             'open_vino', 'frozen_inference_graph.xml')
    model_bin = os.path.join(workspace_dir, dataset, model,
                             'open_vino', 'frozen_inference_graph.bin')
    labels = [l.strip() for l in open(os.path.join(
        workspace_dir, dataset, 'classes.txt')).readlines()]

    # model_xml = '/home/manuel/Bachelor_Arbeit/models_deprecated/faster_rcnn_inception_v2_coco/frozen_inference_graph.xml'
    # model_bin = '/home/manuel/Bachelor_Arbeit/models_deprecated/faster_rcnn_inception_v2_coco/frozen_inference_graph.bin'
    # labels = [l.strip().split('display_name: ')[-1] for l in open(
    #    '/home/manuel/Bachelor_Arbeit/models_deprecated/coco_ssd_inception_v2/classes.txt').readlines() if 'display_name:' in l]
    # test_images_dir = os.path.join(workspace_dir, 'Beispiel_Set', 'validation')
    test_images_dir = os.path.join(workspace_dir, dataset, 'validation')
    #test_images_dir = '/home/manuel/Bachelor_Arbeit/test'
    test_images_dir = '/home/manuel/Bachelor_Arbeit/'

    # collect images
    if os.path.isdir(test_images_dir):
        images = [
            os.path.join(test_images_dir, img) for img in os.listdir(test_images_dir) if img[-3:] == 'jpg']
        print(str(len(images)) + ' images found')
        shuffle(images)
    elif os.path.isfile(test_images_dir) and test_images_dir[-3:] == 'jpg':
        print('one image found')
        images = [test_images_dir]
    else:
        print('wrong input')
        exit()

    ie = IECore()

    # Read IR
    log.info("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
    net = IENetwork(model=model_xml, weights=model_bin)

    img_info_input_blob = None
    feed_dict = {}
    for blob_name in net.inputs:
        if len(net.inputs[blob_name].shape) == 4:
            input_blob = blob_name
        elif len(net.inputs[blob_name].shape) == 2:
            img_info_input_blob = blob_name
        else:
            raise RuntimeError("Unsupported {}D input layer '{}'. Only 2D and 4D input layers are supported"
                               .format(len(net.inputs[blob_name].shape), blob_name))

    assert len(net.outputs) == 1, "Demo supports only single output topologies"

    out_blob = next(iter(net.outputs))
    log.info("Loading IR to the plugin...")
    exec_net = ie.load_network(
        network=net, num_requests=2, device_name='MYRIAD')
    # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    if img_info_input_blob:
        feed_dict[img_info_input_blob] = [h, w, 1]

    cur_request_id = 0
    next_request_id = 1

    log.info("Starting inference in async mode...")
    is_async_mode = True
    render_time = 0

    frame = cv2.imread(images[0])
    initial_h, initial_w = frame.shape[: 2]

    for img_path in images:

        if is_async_mode:
            next_frame = cv2.imread(img_path)
            next_initial_h, next_initial_w = next_frame.shape[: 2]

        else:
            frame = cv2.imread(img_path)
            initial_h, initial_w = frame.shape[: 2]

        # Main sync point:
        # in the truly Async mode we start the NEXT infer request, while waiting for the CURRENT to complete
        # in the regular mode we start the CURRENT request and immediately wait for it's completion
        inf_start = time.time()
        if is_async_mode:
            in_frame = cv2.resize(next_frame, (w, h))
            # Change data layout from HWC to CHW
            in_frame = in_frame.transpose((2, 0, 1))
            in_frame = in_frame.reshape((n, c, h, w))
            feed_dict[input_blob] = in_frame
            exec_net.start_async(request_id=next_request_id, inputs=feed_dict)
        else:
            in_frame = cv2.resize(frame, (w, h))
            # Change data layout from HWC to CHW
            in_frame = in_frame.transpose((2, 0, 1))
            in_frame = in_frame.reshape((n, c, h, w))
            feed_dict[input_blob] = in_frame
            exec_net.start_async(request_id=cur_request_id, inputs=feed_dict)
        if exec_net.requests[cur_request_id].wait(-1) == 0:
            inf_end = time.time()
            det_time = inf_end - inf_start

            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]
            for obj in res[0][0]:
                # Draw only objects when probability more than specified threshold
                if obj[2] > 0.5:
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    class_id = int(obj[1])
                    # Draw box and label\class_id
                    color = (min(class_id * 12.5, 255),
                             min(class_id * 7, 255), min(class_id * 5, 255))
                    cv2.rectangle(frame, (xmin, ymin),
                                  (xmax, ymax), (255, 255, 0), 2)
                    det_label = labels[class_id - 1] if labels else str(
                        class_id)
                    cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 0), 1)

                    print(det_label, obj[2])

            # Draw performance stats
            inf_time_message = "Inference time: N\A for async mode" if is_async_mode else \
                "Inference time: {:.3f} ms".format(det_time * 1000)
            render_time_message = "OpenCV rendering time: {:.3f} ms".format(
                render_time * 1000)
            async_mode_message = "Async mode is on. Processing request {}".format(cur_request_id) if is_async_mode else \
                "Async mode is off. Processing request {}".format(
                    cur_request_id)

            cv2.putText(frame, inf_time_message, (15, 15),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)
            cv2.putText(frame, render_time_message, (15, 30),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)
            cv2.putText(frame, async_mode_message, (10, int(initial_h - 20)), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (10, 10, 200), 1)

        #
        render_start = time.time()
        cv2.imshow("Detection Results", frame)
        render_end = time.time()
        render_time = render_end - render_start

        if is_async_mode:
            cur_request_id, next_request_id = next_request_id, cur_request_id
            frame = next_frame
            initial_w = next_initial_w
            initial_h = next_initial_h

        key = cv2.waitKey(0)
        if key == 27:
            break
        if key == 113:
            is_async_mode = not is_async_mode
            log.info("Switched to {} mode".format(
                "async" if is_async_mode else "sync"))

    cv2.destroyAllWindows()


if __name__ == '__main__':
    sys.exit(main() or 0)
