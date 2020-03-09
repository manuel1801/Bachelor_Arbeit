from openvino.inference_engine import IENetwork, IECore
import numpy as np
import time
import sys
import os
import cv2


class InferenceModel:
    def __init__(self, device='MYRIAD'):
        self.device = device

    def create_exec_infer_model(self, ie, net, model_xml, model_bin, exported_model, num_requests):

        # return ExecInferModel()
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

        out_blob = next(iter(net.outputs))

        if os.path.isfile(exported_model):  # found exported mode
            print('found model to import')
            exec_net = ie.import_network(
                model_file=exported_model, device_name='MYRIAD',
                num_requests=num_requests)
        else:
            print('creating exec model')
            exec_net = ie.load_network(
                network=net, num_requests=num_requests, device_name=self.device)
            exec_net.export(exported_model)

        n, c, h, w = net.inputs[input_blob].shape
        if img_info_input_blob:
            feed_dict[img_info_input_blob] = [h, w, 1]

        return ExecInferModel(exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests)


class ExecInferModel:
    def __init__(self, exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests):
        self.exec_net = exec_net
        self.input_blob = input_blob
        self.out_blob = out_blob
        self.feed_dict = feed_dict
        self.n = n
        self.c = c
        self.h = h
        self.w = w
        self.num_requests = num_requests

    def infer_frames(self, buffer):

        results = []

        for req_idx in range(self.num_requests):

            status = self.exec_net.requests[req_idx].wait(0)

            if status == 0:

                results.append(
                    self.exec_net.requests[req_idx].outputs[self.out_blob])

            if (status == 0 or status == -11) and len(buffer) > 0:
                # start new inference

                in_frame = cv2.resize(buffer.pop(), (self.w, self.h))
                in_frame = in_frame.transpose((2, 0, 1))
                in_frame = in_frame.reshape(
                    (self.n, self.c, self.h, self.w))

                self.feed_dict[self.input_blob] = in_frame

                self.exec_net.start_async(
                    request_id=req_idx, inputs=self.feed_dict)

        return results
