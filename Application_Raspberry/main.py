
import detection_v3 as detection
import connection_ssh as connection
import os
import cv2
import numpy as np
import sys
from datetime import datetime
from time import time, sleep


# Settings:
#import picamera.array
#import picamera


password = 'animalsdetection'

raspi = False

buffer_size = 200    # zum zwischen speichern wenn infer langsamer stream
threshhold = 0.7     # Für Detections
num_requests = 3     # anzahl paralleler inferenz requests, recommended:3
send_results = False  # falls nein wird local gespeichert)
send_email = False   #
send_all_every = 100  # wie oft alle detections senden (in sekunden, 0 für nie)

# nach wie vielen detections einer klasse save and send
# n_save = 300       # für SSDs mit ca 30 FPS
n_save = 10        # für Faster R-CNNs mit ca 0,7 FPS


if raspi:
    user = 'pi'
    remote_user = 'manuel'
    remote_divice_name = 'ssh-Pc'
    view_result = False
else:
    user = 'manuel'
    remote_user = 'pi'
    remote_divice_name = 'ssh-Pi'
    view_result = False


workspace_dir = os.path.join('/home', user, 'Bachelor_Arbeit')
local_output_dir = os.path.join(workspace_dir,
                                'Application_Raspberry/detected')

remote_output_dir = os.path.join(
    '/home', remote_user, 'Bachelor_Arbeit', 'Application_Raspberry/detected')


assert os.path.isdir(local_output_dir)

models_dir = os.path.join(workspace_dir, 'Application_Raspberry/models')
assert os.path.isdir(models_dir)


# SSH Connection Objekt anlegen
if send_results:
    conn = connection.SSHConnect()


# Ausgabe zur Model auswahl
models = []
for i, m in enumerate(os.listdir(models_dir)):
    models.append(m)
    print(i, m)
#model_dir = os.path.join(models_dir, models[int(input())])
# model_dir = os.path.join(models_dir, 'samples_faster_rcnn_inception')
model_dir = os.path.join(models_dir, 'samples_ssd_inception')
# model_dir = os.path.join(models_dir, 'animals_faster_rcnn_inception')
# model_dir = os.path.join(models_dir, 'animals_ssd_inception')

print('selected model: ', model_dir)
assert os.path.isdir(model_dir)


# Load Model to Device
infer_model = detection.InferenceModel(device='MYRIAD')


exec_model = infer_model.create_exec_infer_model(
    model_dir, local_output_dir, num_requests)
retry = 0
while not exec_model:
    print('could not create exec net. try again ', str(retry), '. time.')
    sleep(1)
    exec_model = infer_model.create_exec_infer_model(
        model_dir, local_output_dir, num_requests)
    if retry > 10:
        exit()


del infer_model


# init motion detector
motion_detector = detection.MotionDetect()
motion_frames = []


# Init Cam
if raspi:
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.saturation = -75
    camera.rotation = 180
    capture_empty = np.empty((480, 640, 3), dtype=np.uint8)

else:
    cap = cv2.VideoCapture(0)


# interne variablen (nicht ändern)
no_detections = 0
send_time = time()
logged_in, connected, send_request = False, False, False
save_all = False
has_motion = False
del_idx = 1
n_infered = 0
try_camera = 0

while True:

    # Capture Frame
    if raspi:
        try:
            camera.capture(capture_empty, 'bgr', use_video_port=True)
        except:
            sleep(2)
            if try_camera < 5:
                try_camera += 1
                continue
            break

        capture = np.copy(capture_empty)
    else:
        ret, capture = cap.read()
        if not ret:
            break

    # Detect Motion in Captured Frame and save to buffer
    if motion_detector.detect_motion(capture):
        has_motion = True
        motion_frames.insert(0, capture)
        if len(motion_frames) >= buffer_size:
            del motion_frames[-del_idx]
            if del_idx < len(motion_frames):
                del_idx += 1
        else:
            del_idx = 1
    else:
        has_motion = False

    # disconnect from remote device
    if not motion_frames and connected:
        conn.disconnect()
        print('dissconnecting')
        connected = False

    # Send all current Detections
    if send_all_every > 0 and time() - send_time > send_all_every:
        send_time = time()
        save_all = True

    # damit nur zeit in der inferiert wird berüksicktigt
    if n_infered == 0 and not motion_frames:
        start_time = time()
        infered_frames, fps = 0, 0
    else:
        # fps berechnung
        infered_frames += n_infered
        fps = infered_frames / (time() - start_time)

    print('Fps: ' + str(fps)
          + '\tMotion: ' + str(has_motion)
          + '\tBuffer: ' + str(len(motion_frames)) + '/' + str(buffer_size),
          end='\r', flush=True)

    # Infer Frames
    n_infered, n_detected, n_saved = exec_model.infer_frames(
        motion_frames, threshhold, view_result, n_save, save_all)
    # aus 'motion_frames' werden inferierte frames entfernt (call by ref)

    # set send request
    if n_saved > 0:
        save_all = False
        send_request = True

    # Handle infered frames without detections
    if n_infered > 0 and n_detected == 0:
        no_detections += 1
        if no_detections > 20 * max(1, fps):
            print('resetting motion detector')
            motion_detector.reset_background()
            motion_frames = []
            no_detections = 0

            if connected:
                print('disconnection')
                conn.disconnect()
                connected = False
    else:
        no_detections = 0

    # check send request status
    if not send_results or not send_request:
        continue

    # check login status
    if not logged_in:
        print('try to log in')
        logged_in = conn.login(device_name=remote_divice_name)
        if not logged_in:
            print('could not log in')
            continue
        print('logged in')

    # check connection status
    if not connected:
        print('try to connect')
        connected = conn.connect()
        if not connected:
            logged_in = False
            print('could not connect to ', remote_divice_name)
            continue
        print('connected')

    # get remote server and port name
    server, port = connected

    # reset send request and start to send all files in output dir
    send_request = False
    for image in os.listdir(local_output_dir):
        image_path = os.path.join(local_output_dir, image)

        # try to send and delete local file
        if conn.send(server, port, remote_user, password, image_path, remote_output_dir):
            os.remove(image_path)
            print('Successfully send image ', image)

        # when erro: set send request again for next iteration
        else:
            send_request = True
            print('Error while sending ', image)


if view_result:
    cv2.destroyAllWindows()

if send_results:
    conn.disconnect()
