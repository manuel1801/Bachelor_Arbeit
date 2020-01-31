
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

buffer_size = 200  # zum zwischen speichern wenn infer langsamer stream
infer_requests = 3  # für parallele inferenzen
view_results = False  # für raspi ohne monitor ausschalten
threshhold = 0.6
send_all_every = 60  # sec

#workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit')
workspace_dir = '/home/pi/Bachelor_Arbeit/'  # für autostart
models_dir = os.path.join(workspace_dir, 'openvino_models')

print('select model')
selected_model = {}
i = 1
for dataset in os.listdir(models_dir):
    dataset_dir = os.path.join(models_dir, dataset)
    if os.path.isdir(dataset_dir):
        for model in os.listdir(dataset_dir):
            model_dir = os.path.join(dataset_dir, model)
            if os.path.isdir(model_dir):
                selected_model[i] = dataset, model
                print(i, dataset, model)
                i += 1

#model_ind = int(input())
model_ind = 4  # für autostart
print(selected_model[model_ind], ' selected')

model_xml = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.xml')
model_bin = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.bin')

if os.path.isfile(os.path.join(models_dir, selected_model[model_ind][0], 'classes.txt')):
    labels = [l.strip() for l in open(os.path.join(
        models_dir, selected_model[model_ind][0], 'classes.txt')).readlines()]
else:
    labels = None

assert os.path.isfile(model_bin)
assert os.path.isfile(model_xml)

# Load Model to Device
infer_model = detection.InferenceModel()
exec_model = infer_model.create_exec_infer_model(
    model_xml, model_bin, labels, num_requests=3, conn_ip=ip_addr)

# init motion detector
motion_detector = detection.MotionDetect()
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
            frame, rois, threshhold=threshhold, output_dir=os.path.join(workspace_dir,
                                                                        'Application_Raspberry', 'detected'), fps=fps)

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
        exec_model.send_all(os.path.join(
            workspace_dir, 'Application_Raspberry', 'detected'))

cv2.destroyAllWindows()
