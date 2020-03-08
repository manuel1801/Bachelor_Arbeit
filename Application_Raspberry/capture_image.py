import time
import picamera
import numpy as np
import cv2
import os
from datetime import datetime
import sys

res = (640, 480)

camera = picamera.PiCamera()
camera.resolution = res

night = False
if len(sys.argv) > 1:
    night = True
    camera.saturation = -75

camera.rotation = 180

time.sleep(1)

image = np.empty((res[1], res[0], 3), dtype=np.uint8)

camera.cam(image, 'bgr', use_video_port=True)
if night:
    image_name = 'image_night_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S") + 'jpg'
else:
    image_name = 'image_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S") + 'jpg'

cv2.imwrite(os.path.join('/home/pi/Pictures', image_name), image)

cv2.destroyAllWindows()
