import numpy as np
import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBoxesOnImage as bb_on_image
from matplotlib import pyplot as plt
from argparse import ArgumentParser
import cv2
import os

parser = ArgumentParser(add_help=False)
parser.add_argument('-t', '--train_dir', required=False,
                    type=str, default='train/')

args = parser.parse_args()
train_dir = args.train_dir


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


print("press 'b' to quit batch of current class")
print("press 'q' to quit current class")
print("press 'esc' to quit all")
print("press any other key for next image")

for path in os.listdir(train_dir):

    class_dir = train_dir + path + '/'

    image_paths = []
    label_paths = []
    for file in os.listdir(class_dir):
        if os.path.isdir(class_dir + file):  # falls img/label files in unter ordnern

            label_paths += [class_dir + file + '/' + label for label in os.listdir(
                class_dir + file) if label.split('.')[-1] == 'txt']

            image_paths += [class_dir + file + '/' + label for label in os.listdir(
                class_dir + file) if label.split('.')[-1] == 'jpg']

        elif file.split('.')[-1] == 'jpg':  # falls img/label files in einem ordner
            image_paths.append(class_dir + file)

        elif file.split('.')[-1] == 'txt':
            label_paths.append(class_dir + file)

    # image_paths in gleiche Reihenfolge wie label_paths bringen
    image_paths = [image_paths[idx]
                   for idx in list(map(get_index_by_name, label_paths))]

    # bis hier gleich lassen wegen gleicher reihenfolge
    # ab hier list aufsplitten

    batch = 100
    start_idx = 0
    end_idx = start_idx + batch

    for it in range(len(image_paths) // batch + 1):

        image_paths_sub = [ip for ip in image_paths[start_idx:end_idx]]
        if len(image_paths) == 0:
            break
        label_paths_sub = [lp for lp in label_paths[start_idx:end_idx]]
        images = [cv2.imread(image) for image in image_paths_sub]
        labels = [get_bbox_from_file(label) for label in label_paths_sub]

        start_idx += batch
        if start_idx + batch <= len(image_paths):
            end_idx = start_idx + batch
        else:
            end_idx = len(image_paths)

        for i in range(len(images)):
            img_with_box = bb_on_image(
                labels[i], shape=images[i].shape).draw_on_image(images[i], size=5)
            cv2.imshow('Image', img_with_box)
            key = cv2.waitKey(0)

            if key == 113 or key == 27 or 98:  # quit batch
                break

        if key == 113 or key == 27:  # quit class
            break
    if key == 27:  # quit all
        break
