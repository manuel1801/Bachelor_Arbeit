import time
import picamera
import numpy as np
import cv2
import os
from datetime import datetime
import connection

conn = connection.RaspyConnection()
conn.start_server('10.42.0.111')

res = (640, 480)

output_dir = os.path.join(
    os.environ['HOME'], 'object_detection_ncs2', 'captures')

camera = picamera.PiCamera()
camera.resolution = res
camera.saturation = -75
camera.rotation = 180

time.sleep(2)

image = np.empty((res[1], res[0], 3), dtype=np.uint8)
while True:

    conn.receive_data()

    if input() == 'q':
        break

    camera.capture(image, 'bgr', use_video_port=True)
    image_name = 'image_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
    cv2.imwrite(os.path.join(output_dir, image_name + '.png'), image)
    conn.send_data(image_name, 'text')
    conn.send_data(image, 'image')

cv2.destroyAllWindows()
conn.end_connection()
