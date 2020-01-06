import numpy as np
import cv2
import os


image_path = '/home/manuel/Bachelor_Arbeit/dataset/my_images/'

# max größe von höhe oder breite (je nach ausrichtung)
size = 1024


images = [os.path.join(image_path, i) for i in os.listdir(
    image_path)if i[-3:] == 'jpg']


for img_path in images:
    img = cv2.imread(img_path)
    #cv2.imshow('origineal', img)

    h, w = img.shape[:2]
    if w > h:  # quearformat
        ratio = size / float(w)
        dim = (size, int(h * ratio))
    else:  # hochformat
        ratio = size / float(h)
        dim = (int(w * ratio), size)

    img = cv2.resize(img, dim)
    #cv2.imshow('resized', img)
    # print(img.shape)
    # if cv2.waitKey(0) == 113:
    #    break

    cv2.imwrite(img_path, img)

#img = cv2.imread()
