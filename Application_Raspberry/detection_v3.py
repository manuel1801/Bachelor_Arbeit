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

    def create_exec_infer_model(self, model_dir, output_dir, num_requests=2):

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
            try:
                exec_net = self.ie.import_network(
                    model_file=exported_model, device_name=self.device, num_requests=num_requests)
            except:
                return False
        else:
            print('creating exec model')
            try:
                exec_net = self.ie.load_network(
                    network=net, num_requests=num_requests, device_name=self.device)
                exec_net.export(exported_model)

            except:
                return False
        nchw = net.inputs[input_blob].shape

        del net

        if img_info_input_blob:
            feed_dict[img_info_input_blob] = [nchw[2], nchw[3], 1]
        return ExecInferModel(exec_net, input_blob, out_blob, feed_dict, nchw, labels, output_dir)


class ExecInferModel:
    def __init__(self, exec_net, input_blob, out_blob, feed_dict, nchw, labels, output_dir):
        self.exec_net = exec_net
        self.labels = labels
        self.input_blob = input_blob
        self.out_blob = out_blob
        self.feed_dict = feed_dict
        self.n, self.c, self.h, self.w = nchw
        self.current_frames = {}
        self.detected_objects = {}
        self.output_dir = output_dir

    def infer_frames(self, buffer, threshhold=0.6, view_result=True, n_save=20, save_all=False):

        n_infered, n_detected, n_saved = 0, 0, 0

        for inf_img_ind, infer_request in enumerate(self.exec_net.requests):

            res, frame = None, None

            # get infer status for current req number
            status = infer_request.wait(0)

            if status != 0 and status != -11:
                continue

            # get result of current req number
            if inf_img_ind in self.current_frames:
                res = infer_request.outputs[self.out_blob]
                frame = self.current_frames[inf_img_ind]
                n_infered += 1

            # start new infer request
            if len(buffer):
                self.current_frames[inf_img_ind] = buffer.pop()
                in_frame = cv2.resize(
                    self.current_frames[inf_img_ind], (self.w, self.h))
                in_frame = in_frame.transpose((2, 0, 1))
                in_frame = in_frame.reshape(
                    (self.n, self.c, self.h, self.w))
                self.feed_dict[self.input_blob] = in_frame
                infer_request.async_infer(self.feed_dict)

            # process result of curent infer req number
            if res is None or frame is None:
                continue

            height, width = frame.shape[:2]
            for obj in res[0][0]:

                if obj[2] < threshhold:
                    continue

                n_detected += 1

                # get coordinates
                xmin = int(obj[3] * width)
                ymin = int(obj[4] * height)
                xmax = int(obj[5] * width)
                ymax = int(obj[6] * height)

                # get class id
                class_id = int(obj[1])

                # draw box and text into image
                cv2.rectangle(frame, (xmin, ymin),
                              (xmax, ymax), color=(0, 255, 255), thickness=2)

                cv2.putText(frame, self.labels[class_id - 1] + ' ' + str(round(obj[2] * 100, 1)) + '%', (xmin, ymin - 7),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 1)

                # detected_objects -> class_id:(nr, roi, proba)
                if not class_id in self.detected_objects:
                    self.detected_objects[class_id] = [
                        0, frame, obj[2]]
                else:
                    self.detected_objects[class_id][0] += 1
                    if self.detected_objects[class_id][2] < obj[2]:
                        self.detected_objects[class_id][1] = frame
                        self.detected_objects[class_id][2] = obj[2]

                if self.detected_objects[class_id][0] > n_save:
                    n_saved += 1
                    self._save(class_id)
                    del self.detected_objects[class_id]

                if view_result:
                    cv2.imshow('infer result', frame)
                    cv2.waitKey(1)

        if save_all:
            print('saving all')
            for class_id in self.detected_objects.keys():
                self._save(class_id)
                n_saved += 1
            self.detected_objects = {}
        return n_infered, n_detected, n_saved

    def _save(self, class_id):
        class_name = self.labels[class_id - 1]
        print('saving ', class_name)
        time_stamp = datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
        file_name = time_stamp + '_' + class_name + '.jpg'
        image_array = self.detected_objects[class_id][1]
        # save image local
        cv2.imwrite(os.path.join(
            self.output_dir, file_name), image_array)
