from openvino.inference_engine import IENetwork, IECore
import numpy as np
import time
from datetime import datetime
import sys
import os
import cv2


class MotionDetect:
    def __init__(self):
        self.static_back = None

    def detect_motion(self, frame, reset=False):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.static_back is None or reset:
            self.static_back = gray
            return False
        diff_frame = cv2.absdiff(self.static_back, gray)
        thresh_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
        cnts, _ = cv2.findContours(thresh_frame.copy(),
                                   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            return True
        else:
            return False

    def reset_background(self):
        self.static_back = None


class InferenceModel:
    def __init__(self, device='MYRIAD'):
        self.ie = IECore()
        self.device = device

    def create_exec_infer_model(self, model_dir, num_requests=2):

        model_xml = os.path.join(
            model_dir, 'frozen_inference_graph.xml')
        model_bin = os.path.join(
            model_dir, 'frozen_inference_graph.bin')

        exported_model = os.path.join(model_dir, 'exported_model')

        labels = [line.strip() for line in open(
            os.path.join(model_dir, 'classes.txt')).readlines()]

        assert os.path.isfile(model_bin)
        assert os.path.isfile(model_xml)

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

        assert len(
            net.outputs) == 1, "Demo supports only single output topologies"
        out_blob = next(iter(net.outputs))

        if os.path.isfile(exported_model):
            print('found model to import')
            exec_net = self.ie.import_network(
                model_file=exported_model, device_name=self.device, num_requests=num_requests)
        else:
            print('creating exec model')
            exec_net = self.ie.load_network(
                network=net, num_requests=num_requests, device_name=self.device)
            exec_net.export(exported_model)

        n, c, h, w = net.inputs[input_blob].shape
        if img_info_input_blob:
            feed_dict[img_info_input_blob] = [h, w, 1]

        return ExecInferModel(exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests, labels)


class ExecInferModel:
    def __init__(self, exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests, labels):
        self.exec_net = exec_net
        self.labels = labels
        self.input_blob = input_blob
        self.out_blob = out_blob
        self.feed_dict = feed_dict
        self.n = n
        self.c = c
        self.h = h
        self.w = w
        self.num_requests = num_requests
        self.current_frames = {}
        self.detected_objects = {}
        self.no_detections = 0

    def infer_frames(self, buffer):

        results = []

        for req_idx in range(self.num_requests):

            status = self.exec_net.requests[req_idx].wait(0)

            if status == 0 and req_idx in self.current_frames:

                 # get result
                res = self.exec_net.requests[req_idx].outputs[self.out_blob]
                results.append(
                    (res, self.current_frames.pop(req_idx)))

            if (status == 0 or status == -11) and len(buffer) > 0:
                # start new inference
                self.current_frames[req_idx] = buffer.pop()
                in_frame = cv2.resize(
                    self.current_frames[req_idx], (self.w, self.h))

                in_frame = in_frame.transpose((2, 0, 1))

                in_frame = in_frame.reshape(
                    (self.n, self.c, self.h, self.w))

                self.feed_dict[self.input_blob] = in_frame

                self.exec_net.start_async(
                    request_id=req_idx, inputs=self.feed_dict)

        return results

    def prossec_result(self, result, threshhold, output_dir, fps=1, view_result=False):
        res, frame = result
        height, width = frame.shape[:2]
        saved = False
        self.no_detections += 1

        for obj in res[0][0]:
            confidence = obj[2]
            if obj[2] > threshhold:

                self.no_detections = 0

                # get coordinats
                xmin = int(obj[3] * width)
                ymin = int(obj[4] * height)
                xmax = int(obj[5] * width)
                ymax = int(obj[6] * height)

                # get class
                class_id = int(obj[1])
                class_name = self.labels[class_id - 1]

                cv2.rectangle(frame, (xmin, ymin),
                              (xmax, ymax), color=(0, 255, 255), thickness=2)

                cv2.putText(frame, class_name + ' ' + str(round(confidence * 100, 1)) + '%', (xmin, ymin - 7),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 1)

                if view_result:
                    cv2.imshow('infer result', frame)
                    cv2.waitKey(1)

                # detected_objects -> class_id:(nr, roi, proba)
                if not class_id in self.detected_objects:
                    self.detected_objects[class_id] = [0, frame, obj[2]]
                else:
                    self.detected_objects[class_id][0] += 1
                    if self.detected_objects[class_id][2] < obj[2]:
                        self.detected_objects[class_id][1] = frame
                        self.detected_objects[class_id][2] = obj[2]

                # send detected roi of current class after 10 seconds
                if self.detected_objects[class_id][0] > 10 * max(1, fps):
                    print('saving ', class_name)

                    image_name = 'detected_' + class_name + '_' + \
                        datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
                    image_array = self.detected_objects[class_id][1]

                    # save image local
                    cv2.imwrite(os.path.join(
                        output_dir, image_name + '.png'), image_array)

                    saved = True

                    del self.detected_objects[class_id]

        return self.no_detections, saved

    def save_all(self, output_dir):

        print('svaing all')
        # detected_objects -> class_id:(nr, roi, proba)
        class_ids = list(self.detected_objects.keys())
        saved = False
        for class_id in class_ids:

            if self.labels:
                class_name = self.labels[class_id - 1]
            else:
                class_name = 'class id ' + str(class_id)

            print('saving: ', class_name)
            image_name = 'detected_' + class_name + '_' + \
                datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
            image_array = self.detected_objects[class_id][1]

            cv2.imwrite(os.path.join(
                        output_dir, image_name + '.png'), image_array)

            saved = True
            del self.detected_objects[class_id]
        return saved
