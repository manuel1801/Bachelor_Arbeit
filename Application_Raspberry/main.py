
import detection_v3 as detection
import connection_ssh as connection
import os
import cv2
import numpy as np
import sys
import time
from datetime import datetime


# Settings:
import picamera.array
import picamera


password = 'animalsdetection'
raspi = True

if raspi:
    workspace_dir = '/home/pi/Bachelor_Arbeit/'
    remote_user = 'manuel'
    remote_output_dir = '/home/manuel/Bachelor_Arbeit/Application_Raspberry/detected'
    remote_divice_name = 'ssh-Pc'
else:
    workspace_dir = '/home/manuel/Bachelor_Arbeit/'
    remote_user = 'pi'
    remote_output_dir = '/home/pi/Bachelor_Arbeit/Application_Raspberry/detected'
    remote_divice_name = 'ssh-Pi'


output_dir = os.path.join(workspace_dir,
                          'Application_Raspberry', 'detected')
assert os.path.isdir(output_dir)


# conn = connection.SSHConnect()
# device_address = None
# if conn.login(remote_it_user='animals.detection@gmail.com',
#               remote_it_pw=password):  # returns false if wrong user data
#     device_address = conn.get_device_adress(device_name=remote_divice_name)


buffer_size = 200    # zum zwischen speichern wenn infer langsamer stream
infer_requests = 3   # für parallele inferenzen
view_results = False  # für raspi ohne monitor auf False
threshhold = 0.5     # Für Detections
send_all_every = 60  # sec

models_dir = os.path.join(workspace_dir, 'openvino_models')
assert os.path.isdir(models_dir)

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
model_ind = 8  # für autostart model ind hier festlegen
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
    model_xml, model_bin, labels, num_requests=3)

# init motion detector
motion_detector = detection.MotionDetect()
motion_frames = []

# init and login connection script

conn = connection.SSHConnect()
logged_in = conn.login()

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
send_request = False
start_time = None
send_time = time.time()


while True:

    # Capture Frame
    if raspi:
        camera.capture(capture, 'bgr', use_video_port=True)
    else:
        ret, capture = cap.read()
        if not ret:
            break

    # Detect Motion in Captured Frame and save to buffer
    if motion_detector.detect_motion(capture):
        has_motion = True
        motion_frames.insert(0, capture)
        if len(motion_frames) >= buffer_size:
            # print('buffer len ', str(len(motion_frames)))
           # print('del index ', str(del_idx))
           # print('')
            del motion_frames[-del_idx]
            del_idx += 1
        else:
            del_idx = 1
    else:
        has_motion = False

    if not start_time:
        start_time = time.time()

    # Infer Frames
    result = exec_model.infer_frames(motion_frames)

    # Preocess infered Frames
    for rois, frame in result:
        infered_frames += 1
        fps = infered_frames/(time.time() - start_time)

        print('infered frames: ' + str(infered_frames)
              + '\tFps: ' + str(fps)
              + '\tmotione: ' + str(has_motion)
              + '\tbuffer lenght: ' + str(len(motion_frames)), end='\r', flush=True)

        detection, saved = exec_model.prossec_result(
            frame, rois, threshhold, output_dir, fps=fps, view_result=view_results)

        # Handle infered Frames with no detections
        if not detection:
            no_detections += 1

        if no_detections > 15 * fps:  # alle 15 sec
            print('reset motion detector')
            motion_detector.reset_background()
            motion_frames = []
            no_detections = 0

        # Send saved frames to remote Devices
        if not logged_in:  # kein adresse zu senden
            logged_in = conn.login()
            if not logged_in:
                continue

        if saved or send_request:
            print('try to send')
            conn_info = conn.connect()
            if not conn_info:  # verbindung nicht mögl
                print('Error: could not connect to ', remote_divice_name)
                logged_in = False
                continue

            send_request = False
            for image in os.listdir(output_dir):
                image_path = os.path.join(output_dir, image)
                if conn.send(server=conn_info[0], port=conn_info[1], user=remote_user, password=password,
                             file=image_path, path=remote_output_dir):
                    os.remove(image_path)
                    print('Successfully send image ', image)
                else:
                    send_request = True
                    print('Error while sending ', image)
            conn.disconnect(conn_id=conn_info[2])

    # Send all current Detections
    if (time.time() - send_time) > send_all_every:
        send_time = time.time()
        if exec_model.save_all(output_dir):
            send_request = True

if view_results:
    cv2.destroyAllWindows()
