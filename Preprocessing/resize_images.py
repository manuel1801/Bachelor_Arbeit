import numpy as np
import cv2
import os
import sys
import subprocess

# usage: python3 resize_images.py path/to/images/ size

image_dir = sys.argv[1]
if image_dir[-1] == '/':
    image_dir = image_dir[:-1]

size = int(sys.argv[2])

image_dir_new = image_dir + '_resized_' + str(size)

# kopie der Bilder erzeugen
os.system('cp -r ' + image_dir + ' ' + image_dir_new)

# get paths to all image files
pr = subprocess.Popen(['find', image_dir_new, '-name', '*.jpg'],
                      stdout=subprocess.PIPE)

# collect paths in a list
image_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]

for img_path in image_paths:
    img = cv2.imread(img_path)

    if img is None:
        print('None Type at: ', img_path)
        continue

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
