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
parser.add_argument('-n', '--n_max', required=False, type=int, default=3000)
parser.add_argument('-c', '--color', required=False, type=int, default=0)
parser.add_argument('-g', '--geometric', required=False, type=int, default=0)
parser.add_argument('-a', '--all', required=False, type=int, default=1)

args = parser.parse_args()

train_dir = args.train_dir
n_max = args.n_max
color_augmentation = args.color
geometric_augmentation = args.geometric
all_aumenters = args.all


augmenters = [
    iaa.Dropout(p=(0, 0.1)),
    iaa.CoarseDropout((0.01, 0.05), size_percent=0.1),
    iaa.Multiply((0.5, 1.3), per_channel=(0.2)),
    iaa.GaussianBlur(sigma=(0, 5)),
    iaa.AdditiveGaussianNoise(scale=((0, 0.2*255))),
    iaa.ContrastNormalization((0.5, 1.5)),
    iaa.Grayscale(alpha=((0.1, 1))),
    iaa.ElasticTransformation(alpha=(0, 5.0), sigma=0.25),
    iaa.PerspectiveTransform(scale=(0.15)),
    iaa.MultiplyHueAndSaturation((0.7)),

    iaa.Affine(scale=((0.6, 1.2))),
    iaa.Affine(translate_percent=(-0.3, 0.3)),
    iaa.Affine(shear=(-25, 25)),
    iaa.Affine(translate_percent={"x": (-0.3, 0.3), "y": (-0.2, 0.2)}),
    iaa.Fliplr(1),
    iaa.Affine(scale={"x": (0.6, 1.4), "y": (0.6, 1.4)})
]
if all_aumenters > 0:
    some_of_all = iaa.SomeOf(all_aumenters, augmenters)


# pixel manipulation
color_augmenters = [
    iaa.Dropout(p=(0, 0.1)),
    iaa.CoarseDropout((0.01, 0.05), size_percent=0.1),
    iaa.Multiply((0.5, 1.3), per_channel=(0.2)),
    iaa.GaussianBlur(sigma=(0, 5)),
    iaa.AdditiveGaussianNoise(scale=((0, 0.2*255))),
    iaa.ContrastNormalization((0.5, 1.5)),
    iaa.Grayscale(alpha=((0.1, 1))),
    iaa.ElasticTransformation(alpha=(0, 5.0), sigma=0.25),
    iaa.PerspectiveTransform(scale=(0.15)),
    iaa.MultiplyHueAndSaturation((0.7))
]

if color_augmentation > 0:
    some_of_color = iaa.SomeOf(color_augmentation, color_augmenters)

# geometrische manipulation
# kein rotation verwenden, da boxen nur gut bei viertel drehungen passen, sonst oversized
geometric_augmenters = [
    iaa.Affine(scale=((0.6, 1.2))),
    iaa.Affine(translate_percent=(-0.3, 0.3)),
    iaa.Affine(shear=(-25, 25)),
    iaa.Affine(translate_percent={"x": (-0.3, 0.3), "y": (-0.2, 0.2)}),
    iaa.Fliplr(1),
    iaa.Affine(scale={"x": (0.6, 1.4), "y": (0.6, 1.4)})
]
if geometric_augmentation > 0:
    some_of_geometric = iaa.SomeOf(
        geometric_augmentation, geometric_augmenters)


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


def write_bbox_to_file(bboxes, path):
    labels = []
    for bbox in bboxes:
        label = ' '.join((str(bbox.label),
                          str(bbox.x1),
                          str(bbox.y1),
                          str(bbox.x2),
                          str(bbox.y2)))
        labels.append(label)
    with open(path, 'w') as f_label:
        for label in labels:
            f_label.write(label + '\n')
# funktion die eine liste aus BoundingBoxes die zu einem bild gehören in eine label file


for path in os.listdir(train_dir):

    class_finished = False

    print('augmenting ' + path + '...')
    class_dir = os.path.join(train_dir, path) + '/'

    # max anzahl augmentierungen berechnen, damit 'n_max' data erhalten werden
    n_data = len(os.listdir(class_dir)) - 1
    # hier die -1 rausnehmen, dafür aber auf n_max >= n_data prüfen
    #n_aug = round((n_max-n_data) / n_data)
    n_aug = (n_max-1) // n_data

    if n_aug == 0 or n_data >= n_max:
        continue

    # pfade der bilder und label files der aktuellen klasse in liste sammeln
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

    # gesammt liste in teile splicen wegen speicher
    batch = 100
    start_idx = 0
    end_idx = start_idx + batch

    # len of batch weise iterieren
    for it in range(len(image_paths) // batch + 1):

        # liste in von ind bis ind+batchsize splicen
        image_paths_sub = [ip for ip in image_paths[start_idx:end_idx]]
        if len(image_paths) == 0:
            break

        # in neue liste schreiben
        label_paths_sub = [lp for lp in label_paths[start_idx:end_idx]]

        # bilder und labels aus pfaden der neuen listen laden
        images = [cv2.imread(image) for image in image_paths_sub]
        labels = [get_bbox_from_file(label) for label in label_paths_sub]

        print('batch ' + str(it) + ' von ' +
              str(len(image_paths) // batch + 1))

        # index zum liste splicen erhöhen
        start_idx += batch
        if start_idx + batch <= len(image_paths):
            end_idx = start_idx + batch
        else:
            end_idx = len(image_paths)

        # augmenter durchiterieren und auf images/labels anewnden

        for i_aug in range(n_aug):

            print('augmenting ' + path + str(i_aug+1) + ' von ' + str(n_aug))

            if all_aumenters > 0:
                images_aug, labels_aug = some_of_all(
                    images=images, bounding_boxes=labels)
            else:
                images_aug, labels_aug = some_of_color(
                    images=images, bounding_boxes=labels)
                images_aug, labels_aug = some_of_geometric(
                    images=images_aug, bounding_boxes=labels_aug)

            for i in range(len(image_paths_sub)):

                # break wenn n_max erreicht
                if it * len(image_paths_sub) * n_aug + len(image_paths_sub) * i_aug + i + n_data >= n_max:
                    class_finished = True
                    break

                # remove/clip bboxes outside the image
                bounding_box_on_image = bb_on_image(
                    labels_aug[i], shape=images_aug[i].shape)
                labels_aug[i] = bounding_box_on_image.remove_out_of_image(
                ).clip_out_of_image().bounding_boxes

                # augmentierten images/labels als datei in gleichen ordner schreiben
                write_bbox_to_file(
                    labels_aug[i], label_paths_sub[i][:-4] + '_augmented_' + str(i_aug) + label_paths_sub[i][-4:])
                cv2.imwrite(image_paths_sub[i][:-4] + '_augmented_' + str(i_aug) +
                            image_paths_sub[i][-4:], images_aug[i])

            if class_finished:
                break
        if class_finished:
            break
