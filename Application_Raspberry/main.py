
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


password = 'helloworld'
raspi = True


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


buffer_size = 200    # zum zwischen speichern wenn infer langsamer stream
threshhold = 0.5     # Für Detections
send_all_every = 60  # sec
num_requests = 3     # anzahl paralleler inferenz requests, recommended:3
send_results = True

if send_results:
    conn = connection.SSHConnect()

models_dir = os.path.join(workspace_dir, 'Application_Raspberry/models')
assert os.path.isdir(models_dir)

models = []
for i, m in enumerate(os.listdir(models_dir)):
    models.append(m)
    print(i, m)
model_dir = os.path.join(models_dir, models[int(input())])
# model_dir = os.path.join(models_dir, models[2])

print('selected model: ', model_dir)
assert os.path.isdir(model_dir)


# Load Model to Device
infer_model = detection.InferenceModel()
exec_model = infer_model.create_exec_infer_model(
    model_dir, num_requests=num_requests)


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


infered_frames, fps = 0, 1
start_time, send_time = time.time(), time.time()
logged_in, connected, send_request = False, False, False


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
            del motion_frames[-del_idx]
            del_idx += 1
        else:
            del_idx = 1
    else:
        has_motion = False

    if not motion_frames and connected:
        conn.disconnect()
        print('dissconnecting')
        connected = False

    # Infer Frames
    results = exec_model.infer_frames(motion_frames)

    send_request = False

    # Preocess infered Frames
    for result in results:
        infered_frames += 1
        fps = infered_frames/(time.time() - start_time)
        # fps berechnung stimmt nicht wenn zeitweise
        # keine inferenz
        print('infered frames: ' + str(infered_frames)
              + '\tFps: ' + str(fps)
              + '\tmotione: ' + str(has_motion)
              + '\tbuffer lenght: ' + str(len(motion_frames)), end='\r', flush=True)

        no_detections, saved = exec_model.prossec_result(
            result, threshhold, local_output_dir, fps=fps, view_result=view_result)

        if saved:
            send_request = True

        if no_detections > 20 * max(1, fps):
            print('reset background')
            motion_detector.reset_background()
            motion_frames = []
            exec_model.no_detections = 0

            if connected:
                print('disconnection')
                conn.disconnect()
                connected = False

    # Send all current Detections
    if send_results and (time.time() - send_time) > send_all_every:
        send_time = time.time()

        if exec_model.save_all(local_output_dir):
            send_request = True

    if send_results and send_request:

        if not logged_in:
            print('try to log in')
            logged_in = conn.login(device_name=remote_divice_name)
            if not logged_in:
                print('could not log in')
                continue
            print('logged in')

        if not connected:
            print('try to connect')
            connected = conn.connect()
            if not connected:
                logged_in = False
                print('could not connect to ', remote_divice_name)
                continue
            print('connected')

        server, port = connected

        send_request = False
        for image in os.listdir(local_output_dir):
            image_path = os.path.join(local_output_dir, image)

            if conn.send(server, port, remote_user, password, image_path, remote_output_dir):
                os.remove(image_path)
                print('Successfully send image ', image)
            else:
                send_request = True
                print('Error while sending ', image)

if view_result:
    cv2.destroyAllWindows()

if send_results:
    conn.disconnect()
