from openvino.inference_engine import IENetwork, IECore
import numpy as np
import time
from datetime import datetime
import sys
import os
import cv2
import connection


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

    def create_exec_infer_model(self, model_xml, model_bin, labels=None, num_requests=2, conn_ip=None):

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

        return ExecInferModel(exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests, labels, conn_ip)


class ExecInferModel:
    def __init__(self, exec_net, input_blob, out_blob, feed_dict, n, c, h, w, num_requests, labels, conn_ip):
        self.exec_net = exec_net
        self.conn_ip = conn_ip
        self.conn = connection.RaspyConnection()
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

    def prossec_result(self, frame, res, threshhold, output_dir, fps=1):

        height, width = frame.shape[:2]
        detection = False

        for obj in res[0][0]:
            if obj[2] > threshhold:
                detection = True
                # print(self.initial_w)
                # box koordinaten bezogen auf original image size bestimmen
                xmin = int(obj[3] * width)
                ymin = int(obj[4] * height)
                xmax = int(obj[5] * width)
                ymax = int(obj[6] * height)

                # id des erkannten objekts
                class_id = int(obj[1])

                # box einzeichnen
                # color = (min(class_id * 12.5, 255),
                #          min(class_id * 7, 255), min(class_id * 5, 255))
                color = (0, 255, 0)

                cv2.rectangle(frame, (xmin, ymin),
                              (xmax, ymax), color, 2)

                # label dazu schreiben
                if self.labels:
                    det_label = self.labels[class_id - 1]
                else:
                    det_label = 'class id ' + str(class_id)
                cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

                # detected_objects -> class_id:(nr, roi, proba)
                if not class_id in self.detected_objects:
                    # print(
                        #    'SERVER_INFO: adding new class: ' + det_label + ' to list')
                        # self.detected_objects[class_id] = [
                        #     0, frame[max(0, ymin-20):min(height, ymax+20), max(0, xmin-20):min(width, xmax+20)], obj[2]]
                    self.detected_objects[class_id] = [0, frame, obj[2]]
                else:
                    self.detected_objects[class_id][0] += 1
                    # print('SERVER_INFO: detected class: ' + det_label +
                    #      ' again. Nr of detections: ' + str(self.detected_objects[class_id][0]))
                    if self.detected_objects[class_id][2] < obj[2]:
                            #    print(
                            #        'SERVER_INFO: replaced class: ' + det_label + ' because of higher probability')
                            # self.detected_objects[class_id][1] = frame[max(
                            #     0, ymin-20):min(height, ymax+20), max(0, xmin-20):min(width, xmax+20)]
                        self.detected_objects[class_id][1] = frame
                        self.detected_objects[class_id][2] = obj[2]

                    # send detected roi of current class after 10 detections
                if self.detected_objects[class_id][0] > 10 * fps:
                    print('SERVER_INFO: Class ' + det_label +
                          ' reached max detections. ==> try to send SEND')

                    image_name = 'detected_' + det_label + '_' + \
                        datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
                    image_array = self.detected_objects[class_id][1]

                    try:
                        self.conn.start_client(self.conn_ip)
                        self.conn.send_data(image_name, 'text')
                        self.conn.send_data(image_array, 'image')
                        self.conn.end_connection()
                        print('sending succesfull')
                    except:
                        cv2.imwrite(os.path.join(
                            output_dir, image_name + '.png'), image_array)

                    del self.detected_objects[class_id]

        if detection:
            return frame
        return None

    def send_all(self, output_dir):

        print('sending all')
        # detected_objects -> class_id:(nr, roi, proba)
        class_ids = list(self.detected_objects.keys())
        for class_id in class_ids:

            if self.labels:
                det_label = self.labels[class_id - 1]
            else:
                det_label = 'class id ' + str(class_id)

            print('sending: ', det_label)
            image_name = 'detected_' + det_label + '_' + \
                datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
            image_array = self.detected_objects[class_id][1]

            try:
                self.conn.start_client(self.conn_ip)
                self.conn.send_data(image_name, 'text')
                self.conn.send_data(image_array, 'image')
                self.conn.end_connection()
                print('sending succesfull')
            except:
                cv2.imwrite(os.path.join(
                    output_dir, image_name + '.png'), image_array)
                print('could not connect to server. Saved image locally')

            del self.detected_objects[class_id]

    def view_result(self, capture, processed_frame,  t_capture_str=None,
                    t_infer_str=None, has_motion=None, len_motion_frames=None, buffer_size=None):

        both_frames = np.hstack((capture, processed_frame))
        if t_capture_str:
            cv2.putText(both_frames, 'time: ' + t_capture_str, (15, 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)
        if has_motion:
            cv2.putText(both_frames, 'motion: ' + str(has_motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)
        if len_motion_frames:
            cv2.putText(both_frames, 'buffer: (' + str(len_motion_frames) + '/' + str(buffer_size) + ')', (640 + 15, 25), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)
        if t_infer_str:
            cv2.putText(both_frames, 'time: ' + t_infer_str, (640 + 15, 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)

        cv2.imshow('strem', both_frames)

        return cv2.waitKey(delay=1)


def main():
    pass


if __name__ == "__main__":
    main()
