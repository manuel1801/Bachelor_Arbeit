import numpy as np
import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBoxesOnImage as bb_on_image
from matplotlib import pyplot as plt
from argparse import ArgumentParser
import cv2
import os

'''
usage:
python3 data_augmentation.py -t path/to/train.py -n n_max_samples

train ordner muss unterordner der einzelnen klassen enthalten.
unterordner enthalten bilder und label files, entweder in seperaten oder gleichen ordner
'''

'''
ToDo:
wenn --n_max gesetz, dann wie bisher, wenn nicht definiert wird alle classen mit allen augmentern augmentieren

del_augmented mit dazu nehmen um wahlweise beim ausführen entweder vorhandene augmentierungen zu löschen oder bei zu behalten
oder script nur für augmentierte löschen ausführen

'''


parser = ArgumentParser(add_help=False)
parser.add_argument('-t', '--train_dir', required=False,
                    type=str, default='train/')
parser.add_argument('-n', '--n_max', required=False, type=int, default=2000)
args = parser.parse_args()

train_dir = args.train_dir
n_max = args.n_max

# liste mit anzuwendenden augmentern
augmenters = [[iaa.Affine(translate_percent=(-0.2, 0.2)), iaa.Affine(rotate=(-30, 30))],
              [iaa.Affine(scale=0.8), iaa.Affine(
                  translate_percent={"x": (-0.2, 0.2)})],
              [iaa.Affine(scale=(1.4)), iaa.GaussianBlur(sigma=(0, 3.0))],
              [iaa.Fliplr(1), iaa.Affine(
                  translate_percent={"y": (-0.2, 0.2)})],
              [iaa.Affine(rotate=(-45, 45))],
              [iaa.Affine(translate_percent=(-0.3, 0.3)),
               iaa.Affine(rotate=(-20, 20))],
              [iaa.Affine(scale=0.6), iaa.Affine(
                  translate_percent={"x": (-0.4, 0.4)})],
              [iaa.Affine(scale=(1.6)), iaa.GaussianBlur(sigma=(0, 2.0))],
              [iaa.Fliplr(1), iaa.Affine(scale=0.6), iaa.Affine(
                  translate_percent={"y": (-0.4, 0.4)})],
              [iaa.Affine(rotate=(-55, 55))]]


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

    print('augmenting ' + path + '...')
    class_dir = train_dir + path + '/'

    # max anzahl augmentierungen berechnen, damit 'n_max' data erhalten werden
    n_data = len(os.listdir(class_dir)) - 1
    # hier die -1 rausnehmen, dafür aber auf n_max >= n_data prüfen
    n_aug = round(n_max / n_data)
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
        for i_aug, augmenter in enumerate(augmenters):

            # wenn max augmentierungen erreicht abbrechen
            if i_aug == n_aug:
                break

            print('augmenting ' + path + str(i_aug+1) + ' von ' + str(n_aug))

            # images/labels augmentieren
            seq = iaa.Sequential(augmenter)
            images_aug, labels_aug = seq(images=images, bounding_boxes=labels)

            for i in range(len(image_paths_sub)):

                # break wenn n_max erreicht
                if i_aug * len(image_paths_sub) + i + n_data >= n_max:
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
