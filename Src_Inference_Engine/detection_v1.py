#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import cv2
import logging as log
import numpy as np
import time
import datetime
import connection
from openvino.inference_engine import IENetwork, IECore

#import picamera
#import picamera.array


class Inference:

    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.model_dir = os.path.join(self.workspace_dir, 'models')
        assert os.path.isdir(self.model_dir)
        print('Inference initialized')
        self.static_back = None

    def load_plugin(self, dataset, model):

        model_xml = os.path.join(
            self.model_dir, dataset, model, 'frozen_inference_graph.xml')
        model_bin = os.path.join(self.model_dir, dataset, model,
                                 'frozen_inference_graph.bin')
        self.labels_map = [l.strip() for l in open(os.path.join(
            self.model_dir, dataset, 'classes.txt')).readlines()]

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
        self.exec_net = ie.load_network(
            network=net, num_requests=2, device_name='MYRIAD')

        # Read and pre-process input image
        self.n, self.c, self.h, self.w = net.inputs[self.input_blob].shape

        if img_info_input_blob:
            self.feed_dict[img_info_input_blob] = [self.h, self.w, 1]

        self.cur_request_id = 0
        self.next_request_id = 1

        self.frame = np.ones((480, 640, 3))
        # print(type(self.frame))
        self.initial_h, self.initial_w = self.frame.shape[:2]

        print('plugin initialized')

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

    def infer_stream_webcam(self, input_stream, send_results=False, threshhold=0.5, buffer_size=100):
        if send_results:
            conn = connection.RaspyConnection()
            conn.start_server()
            detected_objects = {}

        cap = cv2.VideoCapture(input_stream)
        reset = False
        images_to_infer = []
        max_images_ro_infer = buffer_size
        remove_ind = 1
        last_frame_processed = False
        motion = False
        infered_frame = np.zeros((480, 640, 3))
        t_capture, t_infer, buffer = 0, 0, 0
        t_infer_str = ''

        while cap.isOpened():

            ret, capture = cap.read()
            # print(capture.shape)
            if not ret:
                break
            if send_results:
                conn.receive_data()  # um clients zu adden

            # ab hier video src unabhängig

            if self.detect_motion(capture, reset=reset):  # bewegung erkannt

                motion = True
                # capture frame in jedem fall hinzufügen
                images_to_infer.insert(0, capture)

                # list mit zu inf frame hat max erreicht
                if len(images_to_infer) >= max_images_ro_infer:
                    # von hinten (älteste frame) beginend jeden zweiten frame aus liste löschen
                    del images_to_infer[-remove_ind]
                    remove_ind += 1
                else:
                    remove_ind = 1  # oder -=1 oder gar nicht??

            else:
                motion = False

            # status von frame das akuell inferiert wird abfragen mit timeout=0s
            req_status = self.exec_net.requests[self.cur_request_id].wait(0)
            # OK = 0
            # INFER_NOT_STARTED = -11
            # RESULT_NOT_READY = -9

            if req_status == 0 or req_status == -11:
                # next_frame aus liste vorbereiten
                if images_to_infer:

                    # wenn liste nicht leer hinterstes frame nehmen
                    next_frame = images_to_infer.pop()
                    next_initial_h, next_initial_w = next_frame.shape[:2]

                    # shape von: HWC zu NCHW
                    in_frame = cv2.resize(next_frame, (self.w, self.h))
                    in_frame = in_frame.transpose((2, 0, 1))
                    in_frame = in_frame.reshape(
                        (self.n, self.c, self.h, self.w))
                    self.feed_dict[self.input_blob] = in_frame

                    # starte asychronen inferez request für next_frame
                    # heir infer start
                    self.exec_net.start_async(
                        request_id=self.next_request_id, inputs=self.feed_dict)
                    last_frame_processed = False

                # wenn frame processed wurde
                if req_status != -11 and not last_frame_processed:

                    # erg der inferenz auslesen
                    res = self.exec_net.requests[self.cur_request_id].outputs[self.out_blob]

                    # alle boxen durchiterieren
                    for obj in res[0][0]:

                        # liegt erkennung über best threshhold
                        if obj[2] > threshhold:

                            # print(self.initial_w)

                            # box koordinaten bezogen auf original image size bestimmen
                            xmin = int(obj[3] * self.initial_w)
                            ymin = int(obj[4] * self.initial_h)
                            xmax = int(obj[5] * self.initial_w)
                            ymax = int(obj[6] * self.initial_h)

                            # id des erkannten objekts
                            class_id = int(obj[1])

                            # box einzeichnen
                            color = (min(class_id * 12.5, 255),
                                     min(class_id * 7, 255), min(class_id * 5, 255))

                            cv2.rectangle(self.frame, (xmin, ymin),
                                          (xmax, ymax), color, 2)

                            # label dazu schreiben
                            det_label = self.labels_map[class_id - 1]
                            cv2.putText(self.frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

                            # send rois:
                            if send_results:
                                # detected_objects -> class_id:(nr, roi, proba)
                                if not class_id in detected_objects:
                                    print(
                                        'SERVER_INFO: adding new class: ' + det_label + ' to list')
                                    detected_objects[class_id] = [
                                        0, self.frame[ymin:ymax, xmin:xmax], obj[2]]
                                else:
                                    detected_objects[class_id][0] += 1
                                    print('SERVER_INFO: detected class: ' + det_label +
                                          ' again. Nr of detections: ' + str(detected_objects[class_id][0]))
                                    if detected_objects[class_id][2] < obj[2]:
                                        print(
                                            'SERVER_INFO: replaced class: ' + det_label + ' because of higher probability')
                                        detected_objects[class_id][1] = self.frame[ymin:ymax, xmin:xmax]
                                        detected_objects[class_id][2] = obj[2]

                                # send detected roi of current class after 10 detections
                                if detected_objects[class_id][0] > 10:
                                    print('SERVER_INFO: Class ' + det_label +
                                          ' reached max detections. ==> SEND')
                                    dt = str(datetime.datetime.now()
                                             ).replace(' ', '_')
                                    conn.send_data(
                                        dt + '_' + det_label, 'text')
                                    conn.send_data(
                                        detected_objects[class_id][1], 'image')
                                    del detected_objects[class_id]

                    # erkanntes bild abspeichern
                    # cv2.imwrite(os.path.join(
                    #     self.workspace_dir, 'results'), self.frame)
                    infered_frame = self.frame
                    # jetzt ist ergebnis in self.frame und kann hier verwendet werden.

                    # next frame (wird gerade inferiert) in frame (wird im nächsten cycle processed) schreiben
                    self.frame = next_frame
                    self.initial_w = next_initial_w
                    self.initial_h = next_initial_h

                    # falls liste leer, ist im nächsten cycle nichts mehr in res
                    if not images_to_infer:
                        last_frame_processed = True

                    t_infer_str = str(
                        round(((time.time() - t_infer) * 1000), 2))
                    t_infer = time.time()

                # swithch req_ids
                self.cur_request_id, self.next_request_id = self.next_request_id, self.cur_request_id

            # cv2.putText(capture, 'motion: ' + str(motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
            #             1, (0, 255, 0), 1)

            both_frames = np.hstack((capture, infered_frame))
            cv2.putText(both_frames, 'motion: ' + str(motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)

            cv2.putText(both_frames, 'buffer: (' + str(len(images_to_infer)) + '/' + str(buffer_size) + ')', (640 + 15, 25), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)

            t_capture_str = str(
                round(((time.time() - t_capture) * 1000), 2))
            t_capture = time.time()
            cv2.putText(both_frames, 'time: ' + t_capture_str, (15, 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)
            cv2.putText(both_frames, 'time: ' + t_infer_str, (640 + 15, 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.5, (0, 255, 0), 1)

            # hier noch jwls fps, buffersize zb (55/100), dropping frames und nur links motion
            # hier aktuellen frame und zuletz inferierten stacken und ausgeben
            cv2.imshow('links:capture rechts:inferiert', both_frames)

            key = cv2.waitKey(1)
            if key == 113:
                break
            reset = False
            if key == 32:  # space for reset motion detector
                print('reset motion detect')
                reset = True
        cv2.destroyAllWindows()
        if send_results:
            conn.end_connection()

    def infer_stream_rpicam(self, input_stream, threshhold=0.5, buffer_size=100, send_results=False):
        if send_results:
            conn = connection.RaspyConnection()
            conn.start_server('10.42.0.111')
            detected_objects = {}

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (640, 480)

                reset = False
                images_to_infer = []
                max_images_ro_infer = buffer_size
                remove_ind = 1
                last_frame_processed = False
                motion = False
                infered_frame = np.zeros((480, 640, 3))
                t_capture, t_infer, buffer = 0, 0, 0
                t_infer_str = ''

                while True:
                    camera.capture(stream, 'bgr', use_video_port=True)
                    capture = stream.array

                    msg = conn.receive_data()  # um clients zu adden

                    if self.detect_motion(capture, reset=reset):  # bewegung erkannt

                        motion = True
                        # capture frame in jedem fall hinzufügen
                        images_to_infer.insert(0, capture)

                        # list mit zu inf frame hat max erreicht
                        if len(images_to_infer) >= max_images_ro_infer:
                            # von hinten (älteste frame) beginend jeden zweiten frame aus liste löschen
                            del images_to_infer[-remove_ind]
                            remove_ind += 1
                        else:
                            remove_ind = 1  # oder -=1 oder gar nicht??

                    else:
                        motion = False
                    if msg:
                        if msg[0] == 'getframe':
                            print('sending current frame')
                            send_frame = capture
                            cv2.putText(send_frame, 'motion: ' + str(motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                                        0.5, (0, 255, 0), 1)
                            conn.send_data('current_frame', 'text')
                            conn.send_data(send_frame, 'image')

                        elif msg[0] == 'reset':
                            print('reset motion')
                            reset = True

                    # status von frame das akuell inferiert wird abfragen mit timeout=0s
                    req_status = self.exec_net.requests[self.cur_request_id].wait(
                        0)
                    # OK = 0
                    # INFER_NOT_STARTED = -11
                    # RESULT_NOT_READY = -9

                    if req_status == 0 or req_status == -11:
                        # next_frame aus liste vorbereiten
                        if images_to_infer:

                            # wenn liste nicht leer hinterstes frame nehmen
                            next_frame = images_to_infer.pop()
                            next_initial_h, next_initial_w = next_frame.shape[:2]

                            # shape von: HWC zu NCHW
                            in_frame = cv2.resize(next_frame, (self.w, self.h))
                            in_frame = in_frame.transpose((2, 0, 1))
                            in_frame = in_frame.reshape(
                                (self.n, self.c, self.h, self.w))
                            self.feed_dict[self.input_blob] = in_frame

                            # starte asychronen inferez request für next_frame
                            # heir infer start
                            self.exec_net.start_async(
                                request_id=self.next_request_id, inputs=self.feed_dict)
                            last_frame_processed = False

                        # wenn frame processed wurde
                        if req_status != -11 and not last_frame_processed:

                            # erg der inferenz auslesen
                            res = self.exec_net.requests[self.cur_request_id].outputs[self.out_blob]

                            # alle boxen durchiterieren
                            for obj in res[0][0]:

                                # liegt erkennung über best threshhold
                                if obj[2] > threshhold:

                                    # print(self.initial_w)

                                    # box koordinaten bezogen auf original image size bestimmen
                                    xmin = int(obj[3] * self.initial_w)
                                    ymin = int(obj[4] * self.initial_h)
                                    xmax = int(obj[5] * self.initial_w)
                                    ymax = int(obj[6] * self.initial_h)

                                    # id des erkannten objekts
                                    class_id = int(obj[1])

                                    # box einzeichnen
                                    color = (min(class_id * 12.5, 255),
                                             min(class_id * 7, 255), min(class_id * 5, 255))

                                    cv2.rectangle(self.frame, (xmin, ymin),
                                                  (xmax, ymax), color, 2)

                                    # label dazu schreiben
                                    det_label = self.labels_map[class_id - 1]
                                    cv2.putText(self.frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                                cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

                                    # send rois:
                                    if send_results:
                                        # detected_objects -> class_id:(nr, roi, proba)
                                        if not class_id in detected_objects:
                                            print(
                                                'SERVER_INFO: adding new class: ' + det_label + ' to list')
                                            detected_objects[class_id] = [
                                                0, self.frame[ymin:ymax, xmin:xmax], obj[2]]
                                        else:
                                            detected_objects[class_id][0] += 1
                                            print('SERVER_INFO: detected class: ' + det_label +
                                                  ' again. Nr of detections: ' + str(detected_objects[class_id][0]))
                                            if detected_objects[class_id][2] < obj[2]:
                                                print(
                                                    'SERVER_INFO: replaced class: ' + det_label + ' because of higher probability')
                                                detected_objects[class_id][1] = self.frame[ymin:ymax, xmin:xmax]
                                                detected_objects[class_id][2] = obj[2]

                                        # send detected roi of current class after 10 detections
                                        if detected_objects[class_id][0] > 10:
                                            print('SERVER_INFO: Class ' + det_label +
                                                  ' reached max detections. ==> SEND')
                                            dt = str(datetime.datetime.now()
                                                     ).replace(' ', '_')
                                            conn.send_data(
                                                dt + '_' + det_label, 'text')
                                            conn.send_data(
                                                detected_objects[class_id][1], 'image')
                                            del detected_objects[class_id]

                            # erkanntes bild abspeichern
                            # cv2.imwrite(os.path.join(
                            #     self.workspace_dir, 'results'), self.frame)
                            infered_frame = self.frame
                            # jetzt ist ergebnis in self.frame und kann hier verwendet werden.

                            # next frame (wird gerade inferiert) in frame (wird im nächsten cycle processed) schreiben
                            self.frame = next_frame
                            self.initial_w = next_initial_w
                            self.initial_h = next_initial_h

                            # falls liste leer, ist im nächsten cycle nichts mehr in res
                            if not images_to_infer:
                                last_frame_processed = True

                            t_infer_str = str(
                                round(((time.time() - t_infer) * 1000), 2))
                            t_infer = time.time()

                        # swithch req_ids
                        self.cur_request_id, self.next_request_id = self.next_request_id, self.cur_request_id

                    # cv2.putText(capture, 'motion: ' + str(motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                    #             1, (0, 255, 0), 1)

                    both_frames = np.hstack((capture, infered_frame))
                    cv2.putText(both_frames, 'motion: ' + str(motion), (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (0, 255, 0), 1)

                    cv2.putText(both_frames, 'buffer: (' + str(len(images_to_infer)) + '/' + str(buffer_size) + ')', (640 + 15, 25), cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (0, 255, 0), 1)

                    t_capture_str = str(
                        round(((time.time() - t_capture) * 1000), 2))
                    t_capture = time.time()
                    cv2.putText(both_frames, 'time: ' + t_capture_str, (15, 45), cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (0, 255, 0), 1)
                    cv2.putText(both_frames, 'time: ' + t_infer_str, (640 + 15, 45), cv2.FONT_HERSHEY_COMPLEX,
                                0.5, (0, 255, 0), 1)

                    # hier noch jwls fps, buffersize zb (55/100), dropping frames und nur links motion
                    # hier aktuellen frame und zuletz inferierten stacken und ausgeben
                    # cv2.imshow('links:capture rechts:inferiert', both_frames)

                    key = cv2.waitKey(1)
                    if key == 113:
                        break
                    reset = False
                    if key == 32:  # space for reset motion detector
                        print('reset motion detect')
                        reset = True
                    stream.seek(0)
                    stream.truncate()
                cv2.destroyAllWindows()
                if send_results:
                    conn.end_connection()


def main():
    pass


if __name__ == "__main__":
    main()
