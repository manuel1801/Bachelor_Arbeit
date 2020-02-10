from openvino.inference_engine import IENetwork, IECore
import numpy as np
import sys
import os
import cv2


class InferenceModel:
    def __init__(self, device='MYRIAD'):
        self.ie = IECore()
        self.device = device

    def create_exec_infer_model(self, model_xml, model_bin, labels=None, num_requests=2):

        assert os.path.isfile(model_bin)
        assert os.path.isfile(model_xml)

        net = IENetwork(model=model_xml, weights=model_bin)

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

        assert len(
            net.outputs) == 1, "Demo supports only single output topologies"
        out_blob = next(iter(net.outputs))
        exec_net = self.ie.load_network(
            network=net, num_requests=num_requests, device_name=self.device)
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

    def infer_image(self, image, threshhold=0.7):
        height, width = image.shape[:2]
        in_frame = cv2.resize(image, (self.w, self.h))
        in_frame = in_frame.transpose((2, 0, 1))
        in_frame = in_frame.reshape(
            (self.n, self.c, self.h, self.w))

        self.feed_dict[self.input_blob] = in_frame
        self.exec_net.start_async(
            request_id=0, inputs=self.feed_dict)

        if self.exec_net.requests[0].wait(-1) == 0:
            res = self.exec_net.requests[0].outputs[self.out_blob]

            for obj in res[0][0]:
                if obj[2] > threshhold:
                    xmin = int(obj[3] * width)
                    ymin = int(obj[4] * height)
                    xmax = int(obj[5] * width)
                    ymax = int(obj[6] * height)

                    class_id = int(obj[1])
                    color = (0, 255, 0)
                    cv2.rectangle(image, (xmin, ymin),
                                  (xmax, ymax), color, 2)

                    if self.labels:
                        det_label = self.labels[class_id - 1]
                    else:
                        det_label = 'class id ' + str(class_id)
                    cv2.putText(image, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
        return image
