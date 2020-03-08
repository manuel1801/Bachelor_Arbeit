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
if len(sys.argv) > 2:
    night = True
    camera.saturation = -75

camera.rotation = 180

time.sleep(1)

image = np.empty((res[1], res[0], 3), dtype=np.uint8)

if night:
    image_name = 'image_night_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
else:
    image_name = 'image_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S")

output_dir = '/home/pi/Pictures'
n = int(sys.argv[1])
if n > 1:
    output_dir = os.path.join(output_dir, image_name)
    os.mkdir(os.path.join(output_dir))


for i in range(n):
    camera.capture(image, 'bgr', use_video_port=True)
    cv2.imwrite(os.path.join(output_dir,
                             str(i) + '_' + image_name + '.jpg'), image)


cv2.destroyAllWindows()
