import detection
import connection
import os
import cv2
import numpy as np
import sys
from datetime import datetime
from time import time, sleep
import picamera.array
import picamera


send_results = True
remote_user = 'manuel'
remote_divice_name = 'ssh-Pc'
remote_it_email = 'animals.detection@gmail.com'
password_remote_divece = 'animalsdetection20'
password_remoteit = 'animalsdetection20'
remote_output_dir = os.path.join(
    '/home', remote_user, 'Bachelor_Arbeit', 'Application/detected')
send_email = None


# Wenn erkannte Bilder an ein Remote
# Gerät gesendet werden sollen
# send_result = True und folgende Nutzerdaten definieren
# sonst werden erkannte Bilder lokal in detected/ gespeichert
# send_results = False
# remote_user = ''
# remote_divice_name = ''
# remote_it_email = ''
# password_remote_divece = ''
# password_remoteit = ''
# remote_output_dir = os.path.join('/home', remote_user)
# # optional zum senden von E-Main Benachrichtigung:
# send_email = None    # Ziel E-Mail Adresse


buffer_size = 200    # anzahl an frames die zwischengespeichert werden
threshhold = 0.7     # für die wahrscheinlichkeit mit der eine Erkennung erfolgte
num_requests = 3     # anzahl paralleler inferenz requests,
n_save = 10  # nach wie vielen Erkennungen der gleichen Klasse gespeichert/gesendet werden soll
view_result = False  # anzeigen des Kamera Streams (geht nur mit Monitor)


# Eine der folgenden Listen auswählen
# SSD Modell wird verwendet, wenn das Faster R-CNN Modell nicht laden konnte
# models = ['samples_faster_rcnn_inception', 'samples_ssd_inception']
models = ['animals_faster_rcnn_inception', 'animals_ssd_inception']


# pfad des main.py Scripts
appl_dir = os.path.dirname(sys.argv[0])

# Ordner in den lokal erkannte Bilder abgespeichert werden
local_output_dir = os.path.join(appl_dir, 'detected')
if not os.path.isdir(local_output_dir):
    os.mkdir(local_output_dir)
assert os.path.isdir(local_output_dir)

# Ordner in dem die OpenVino Modelle liegen
models_dir = os.path.join(appl_dir, 'models')
assert os.path.isdir(models_dir)

# SSH Connection Objekt anlegen
if send_results:
    conn = connection.SSHConnect(remote_it_email, password_remoteit)

# Model auf Hardware laden
# zuerst Faster R-CNN, wenn fehler auftritt SSD verwenden.
infer_model = detection.InferenceModel(device='MYRIAD')
for model in models:
    exec_model = infer_model.create_exec_infer_model(
        os.path.join(models_dir, model), local_output_dir, num_requests)
    if exec_model:
        break
    n_save = 200  # für ssd, da schneller inferiert
    threshhold = 0.5
if not exec_model:
    print('error loading model')
    exit()
print('load: ', model)
del infer_model

# Motion Detector anlegen
motion_detector = detection.MotionDetect()
motion_frames = []

# Raspberry Pi kamera einstellen
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.saturation = -75
camera.rotation = 180
capture_empty = np.empty((480, 640, 3), dtype=np.uint8)


# interne Variablen
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
    try:
        camera.capture(capture_empty, 'bgr', use_video_port=True)
    except:
        sleep(2)
        if try_camera < 5:
            try_camera += 1
            continue
        break
    capture = np.copy(capture_empty)

    # Captured Frame auf Bewegung prüfen und im Buffer Speichern
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

    # Wenn Buffer Liste leer Verbindung trennen
    if send_results and not motion_frames and connected:
        conn.disconnect()
        print('dissconnecting')
        connected = False

    # nach 100 Sekunden alle Erkannte, aber nicht
    # gespeicherten Frames abspeichern
    if time() - send_time > 100:
        send_time = time()
        save_all = True

    # Buffer Liste 'motion_frames' zur Inferenz übergeben.
    # Inferierte Frames werden aus der List entfernt (Call by Ref.)
    n_infered, n_detected, n_saved = exec_model.infer_frames(
        motion_frames, threshhold, view_result, n_save, save_all)

    # Send Request aufgeben
    if n_saved > 0:
        save_all = False
        send_request = True

    # Handling von inferierten Frames ohne Erkennung
    if n_infered > 0 and n_detected == 0:
        no_detections += 1

        # Motion Detector Referenz Frame neu setzen
        if no_detections > 50:
            print('resetting motion detector')
            motion_detector.reset_background()
            motion_frames = []
            no_detections = 0

            # Verbindung Trennen
            if send_results and connected:
                print('disconnection')
                conn.disconnect()
                connected = False
    else:
        no_detections = 0

    # Send Request Status abfragen
    if not send_results or not send_request:
        continue

    # E-Mail senden
    if send_email:
        print('sending email')
        msg_str = ''
        for msg in os.listdir(local_output_dir):
            msg_str += msg[:-4] + '\n'
        conn.send_email(send_email, msg_str)

    # login status prüfen
    if not logged_in:
        print('try to log in')
        logged_in = conn.login(device_name=remote_divice_name)
        if not logged_in:
            print('could not log in')
            continue
        print('logged in')

    # connection status prüfen
    if not connected:
        print('try to connect')
        connected = conn.connect()
        if not connected:
            logged_in = False
            print('could not connect to ', remote_divice_name)
            continue
        print('connected')

    # remote server und port auslesen
    server, port = connected

    # Send Request zurücksetzen und mit Senden aller
    # gespeicherten Bilder starten
    send_request = False
    for image in os.listdir(local_output_dir):
        image_path = os.path.join(local_output_dir, image)

        # senden and Datei Lokal löschen
        if conn.send(server, port, remote_user, password_remote_divece, image_path,
                     os.path.join(remote_output_dir, image[:-4] + '_' + model + image[-4:])):

            os.remove(image_path)
            print('Successfully send image ', image)

        # Wenn Fehler auftritt Send-Request wieder setzen
        else:
            send_request = True
            print('Error while sending ', image)


if view_result:
    cv2.destroyAllWindows()

if send_results:
    conn.disconnect()
