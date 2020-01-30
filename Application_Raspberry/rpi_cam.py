import time
import picamera
import numpy as np
import cv2
import os
from datetime import datetime


res = (640, 480)

output_dir = os.path.join(
    os.environ['HOME'], 'object_detection_ncs2', 'output')


camera = picamera.PiCamera()
camera.resolution = res

camera.saturation = -75
camera.rotation = 180

time.sleep(2)

image = np.empty((res[1], res[0], 3), dtype=np.uint8)
while True:
    camera.capture(image, 'bgr', use_video_port=True)

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('capture', image)
    cv2.imshow('capture_gray', image_gray)

    key = cv2.waitKey(1)
    if key == 113:
        break
    if key == 32:
        iamge_name = 'image_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
        cv2.imwrite(os.path.join(output_dir, iamge_name + '.png'), image)
        cv2.imwrite(os.path.join(
            output_dir, iamge_name + '_gray.png'), image_gray)


cv2.destroyAllWindows()
