import numpy as np
import imgaug as ia
from imgaug.augmentables.bbs import BoundingBoxesOnImage as bb_on_image
import cv2
import os
import sys
import subprocess
from random import shuffle


'''
durchsuch rekusiv directory nahch passenden image/label files und zeigt mit box an
Usage: python3 path/to/dir
'''


def get_index_by_name(label_path):
    label_name = '/' + label_path.split('/')[-1][: -3]
    for idx, img_path in enumerate(image_paths):
        if label_name in img_path:
            return idx
# Funktion gibt index des image_path zurück der zu label_path gehört


def get_bbox_from_file(label_file):
    labels = [f.strip() for f in open(label_file).readlines()]
    my_bbs = []
    for label in labels:
        label_content = label.split(' ')
        label_class = label_content[0]
        label_box = np.array(label_content[1:]).astype(np.float64)
        bbox = ia.BoundingBox(
            x1=label_box[0], y1=label_box[1], x2=label_box[2], y2=label_box[3], label=label_class)
        my_bbs.append(bbox)
    return my_bbs
# Funktion die aus einem label file (OpenImages Format) eine liste von ia.BoundinBox Objekte erstellt


path = sys.argv[1]

# get paths to all image files
pr = subprocess.Popen(['find', path, '-name', '*.jpg'],
                      stdout=subprocess.PIPE)

# collect paths in a list
image_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]
# get paths to all image files
pr = subprocess.Popen(['find', path, '-name', '*.txt'],
                      stdout=subprocess.PIPE)

# collect paths in a list
label_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]
shuffle(label_paths)

# sort
image_paths = [image_paths[idx]
               for idx in list(map(get_index_by_name, label_paths))]

print("press 'q' for exit")
for i in range(len(image_paths)):
    bbox = get_bbox_from_file(label_paths[i])
    img = cv2.imread(image_paths[i])
    img_with_box = bb_on_image(
        bbox, shape=img.shape).draw_on_image(img, size=5)
    cv2.imshow('image', img_with_box)
    if cv2.waitKey(0) == 113:
        break

cv2.destroyAllWindows()
