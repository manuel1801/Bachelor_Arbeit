import time
import picamera
import numpy as np
import cv2
import os
from datetime import datetime


res = (640, 480)

output_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/Application_Raspberry/captures')


camera = picamera.PiCamera()
camera.resolution = res

camera.saturation = -75
camera.rotation = 180

time.sleep(2)

image = np.empty((res[1], res[0], 3), dtype=np.uint8)
while True:
    camera.capture(image, 'bgr', use_video_port=True)

    key = cv2.waitKey(1)
    if key == 113:
        break
    if key == 32:
        iamge_name = 'image_' + datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
        cv2.imwrite(os.path.join(output_dir, iamge_name + '.png'), image)


cv2.destroyAllWindows()
