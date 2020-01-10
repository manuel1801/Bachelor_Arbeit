#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import cv2
import logging as log
import numpy as np
import time
from openvino.inference_engine import IENetwork, IECore


class Inference:

    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        print('Inference initialized')

    def load_plugin(self, dataset, model):

        model_xml = os.path.join(self.workspace_dir, dataset, model,
                                 'open_vino', 'frozen_inference_graph.xml')
        model_bin = os.path.join(self.workspace_dir, dataset, model,
                                 'open_vino', 'frozen_inference_graph.bin')
        self.labels_map = [l.strip() for l in open(os.path.join(
            self.workspace_dir, dataset, 'classes.txt')).readlines()]

        assert os.path.isfile(model_bin)
        assert os.path.isfile(model_xml)

        log.info("Creating Inference Engine...")
        ie = IECore()
        log.info("Loading network files:\n\t{}\n\t{}".format(
            model_xml, model_bin))
        net = IENetwork(model=model_xml, weights=model_bin)

        img_info_input_blob = None
        self.feed_dict = {}
        for blob_name in net.inputs:
            if len(net.inputs[blob_name].shape) == 4:
                self.input_blob = blob_name
            elif len(net.inputs[blob_name].shape) == 2:
                img_info_input_blob = blob_name
            else:
                raise RuntimeError("Unsupported {}D input layer '{}'. Only 2D and 4D input layers are supported"
                                   .format(len(net.inputs[blob_name].shape), blob_name))

        assert len(
            net.outputs) == 1, "Demo supports only single output topologies"

        self.out_blob = next(iter(net.outputs))
        log.info("Loading IR to the plugin...")

        t1 = time.time()
        self.exec_net = ie.load_network(
            network=net, num_requests=2, device_name='MYRIAD')
        print(time.time() - t1)

        # Read and pre-process input image
        self.n, self.c, self.h, self.w = net.inputs[self.input_blob].shape

        if img_info_input_blob:
            self.feed_dict[img_info_input_blob] = [self.h, self.w, 1]

        self.cur_request_id = 0
        self.next_request_id = 1

        self.frame = np.ones((600, 600, 3))
        # print(type(self.frame))
        self.initial_h, self.initial_w = self.frame[:2]

    print('plugin initialized')

    def infer_stream(self, input_stream, threshhold, save_image_files=False, save_time_in_sec=5):
        if save_image_files:
            t_start = time.time()
            os.mkdir(os.path.join(self.workspace_dir, 'saved_images'))
        cap = cv2.VideoCapture(input_stream)
        while cap.isOpened():
            ret, next_frame = cap.read()
            if not ret:
                break

            next_initial_w = cap.get(3)
            next_initial_h = cap.get(4)

            self.frame = self.__infer_frame(next_frame, threshhold)

            cv2.imshow("Detection Results", self.frame)
            actual_time = time.time() - t_start
            if save_image_files and actual_time < save_time_in_sec:
                print('saving image to ' + os.path.join(self.workspace_dir,
                                                        'saved_images', 'image_' + str(actual_time) + '.jpg'))
                cv2.imwrite(os.path.join(self.workspace_dir,
                                         'saved_images', 'image_' + str(actual_time) + '.jpg'), self.frame)

            self.cur_request_id, self.next_request_id = self.next_request_id, self.cur_request_id
            self.frame = next_frame
            self.initial_w = next_initial_w
            self.initial_h = next_initial_h

            if cv2.waitKey(1) == 113:
                break

        cv2.destroyAllWindows()

    def infer_image(self, img_path, threshhold):

        next_frame = cv2.imread(img_path)
        next_initial_h, next_initial_w = next_frame.shape[:2]

        ret_frame = self.__infer_frame(next_frame, threshhold)

        self.cur_request_id, self.next_request_id = self.next_request_id, self.cur_request_id
        self.frame = next_frame
        self.initial_w = next_initial_w
        self.initial_h = next_initial_h

        return ret_frame

    def infer_video(self):
        pass

    def __infer_frame(self, next_frame, threshhold):

        inf_start = time.time()

        in_frame = cv2.resize(next_frame, (self.w, self.h))
        # Change data layout from HWC to CHW
        in_frame = in_frame.transpose((2, 0, 1))
        in_frame = in_frame.reshape((self.n, self.c, self.h, self.w))
        self.feed_dict[self.input_blob] = in_frame
        self.exec_net.start_async(
            request_id=self.next_request_id, inputs=self.feed_dict)

        if self.exec_net.requests[self.cur_request_id].wait(-1) == 0:
            inf_end = time.time()
            det_time = inf_end - inf_start
            det_time_str = str(round((det_time * 1000), 2)) + 'ms'
            res = self.exec_net.requests[self.cur_request_id].outputs[self.out_blob]

            for obj in res[0][0]:
                if obj[2] > threshhold:
                    xmin = int(obj[3] * self.initial_w)
                    ymin = int(obj[4] * self.initial_h)
                    xmax = int(obj[5] * self.initial_w)
                    ymax = int(obj[6] * self.initial_h)
                    class_id = int(obj[1])

                    # Draw box and label\class_id
                    color = (min(class_id * 12.5, 255),
                             min(class_id * 7, 255), min(class_id * 5, 255))
                    cv2.rectangle(self.frame, (xmin, ymin),
                                  (xmax, ymax), color, 2)

                    det_label = self.labels_map[class_id - 1] if self.labels_map else str(
                        class_id)
                    cv2.putText(self.frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

            cv2.putText(self.frame, det_time_str, (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                        0.8, (255, 0, 0), 1)
        return self.frame


def main():
    # workspace_dir = '/home/manuel/Bachelor_Arbeit/workspace'

    # inference = Inference(workspace_dir)
    # inference.load_plugin('OI_Animals_Augmented_9_2000',
    #                       'faster_rcnn_inception_v2_coco_2018_01_28_out')
    pass


if __name__ == "__main__":
    main()
