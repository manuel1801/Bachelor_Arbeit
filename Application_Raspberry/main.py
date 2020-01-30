
import detection_v3 as detection
import connection
import os
import cv2
import numpy as np
import sys
import time
from datetime import datetime
import connection

# Settings:
import picamera.array
import picamera
raspi = True
ip_addr = '10.10.73.89'

buffer_size = 100  # zum zwischen speichern wenn infer langsamer stream
infer_requests = 3  # für parallele inferenzen
view_results = False  # für raspi ohne monitor ausschalten
threshhold = 0.6
send_all_every = 60  # sec

model_ind = 2

workspace_dir = '/home/pi/object_detection_ncs2'
workspace_dir = '/home/manuel/Bachelor_Arbeit/Application_Raspberry'

#workspace_dir = '/home/manuel/object_detection_ncs2'
#workspace_dir = os.path.join(os.environ['HOME'], 'object_detection_ncs2')
model = {1: ['Samples', 'ssd_mobilenet_v2'],
         2: ['Samples', 'ssd_inception_v2'],
         3: ['Samples', 'faster_rcnn_inception_v2'],
         4: ['Samples', 'faster_rcnn_inception_v2_gray'],
         5: ['Animals', 'ssd_inception_v2'],
         6: ['Animals', 'faster_rcnn_inception_v2_3000'],
         7: ['Animals', 'faster_rcnn_inception_v2_gray'],
         8: ['Animals', 'faster_rcnn_inception_v2_gray_3000']}

# for m in model.items():
#     print(m)
# print('select model')
# model_ind = int(input())
# print(model[model_ind], ' selected')


# Load Model to Device
infer_model = detection.InferenceModel()
exec_model = infer_model.create_exec_infer_model(
    os.path.join(workspace_dir, 'models'),
    model[model_ind][0],
    model[model_ind][1],
    num_requests=infer_requests,
    conn_ip=ip_addr)


# init motion detector
motion_detector = detection.MotionDetect()  # threshhold
motion_frames = []

has_motion = False
del_idx = 1

# Init Cam
if raspi:
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.saturation = -75
    camera.rotation = 180
    capture = np.empty((480, 640, 3), dtype=np.uint8)

else:
    cap = cv2.VideoCapture(0)


infered_frames = 0
no_detections = 0
start_time = None
send_time = time.time()
key = 0

while True:

    if raspi:
        camera.capture(capture, 'bgr', use_video_port=True)
    else:
        ret, capture = cap.read()
        if not ret:
            break

    # Detect Motion
    if motion_detector.detect_motion(capture):
        has_motion = True
        motion_frames.insert(0, capture)
        if len(motion_frames) >= buffer_size:
            #print('buffer len ', str(len(motion_frames)))
           # print('del index ', str(del_idx))
           # print('')
            del motion_frames[-del_idx]
            del_idx += 1
        else:
            del_idx = 1
    else:
        has_motion = False

    # Infer Frame
    #ret, infered_frame = exec_model.infer_frame_non_blocking(motion_frames)
    if not start_time:
        start_time = time.time()

    result = exec_model.infer_frames(motion_frames)

    for rois, frame in result:
        infered_frames += 1
        fps = infered_frames/(time.time() - start_time)

        print('infered frames: ' + str(infered_frames)
              + '\tFps: ' + str(fps)
              + '\tmotione: ' + str(has_motion)
              + '\tbuffer lenght: ' + str(len(motion_frames)), end='\r', flush=True)

        processed_frame = exec_model.prossec_result(
            frame, rois, threshhold=threshhold, workspace_dir=workspace_dir, fps=fps)

        if processed_frame is None:
            no_detections += 1

        if no_detections > 15 * fps:  # alle 15 sec
            print('10th motion frame with no detection: RESET motion detector' + (' '*10))
            motion_detector.reset_background()
            motion_frames = []
            no_detections = 0

        if view_results:
            cv2.imshow('infer result', processed_frame)
            key = cv2.waitKey(1)

            if key == 32:
                motion_detector.reset_background()

    if key == 113:
        break

    if (time.time() - send_time) > send_all_every:
        send_time = time.time()
        exec_model.send_all(workspace_dir=workspace_dir)


cv2.destroyAllWindows()
