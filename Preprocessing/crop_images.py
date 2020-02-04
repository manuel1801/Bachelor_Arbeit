import numpy as np
import cv2
import os
import sys
import subprocess
import imgaug as ia
from imgaug.augmentables.bbs import BoundingBoxesOnImage as bb_on_image

image_dir = sys.argv[1]
if image_dir[-1] == '/':
    image_dir = image_dir[:-1]


def get_index_by_name(label_path):
    label_name = '/' + label_path.split('/')[-1][: -3]
    for idx, img_path in enumerate(image_paths):
        if label_name in img_path:
            return idx


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


image_dir_crop = image_dir + '_crop'
#image_dir_crop = image_dir
# kopie der Bilder erzeugen
os.system('cp -r ' + image_dir + ' ' + image_dir_crop)

# get paths to all image files
pr = subprocess.Popen(['find', image_dir_crop, '-name', '*.jpg'],
                      stdout=subprocess.PIPE)
# collect paths in a list
image_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]

# get paths to all image files
pr = subprocess.Popen(['find', image_dir_crop, '-name', '*.txt'],
                      stdout=subprocess.PIPE)
# collect paths in a list
label_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]

# sort
image_paths = [image_paths[idx]
               for idx in list(map(get_index_by_name, label_paths))]


for i in range(len(image_paths)):
    bbox = get_bbox_from_file(label_paths[i])
    img = cv2.imread(image_paths[i])
    try:
        h, w = img.shape[:2]
    except:
        print('could not load ', image_paths[i])
        continue

    for n, box in enumerate(bbox):
        add_y = int((box.y2 - box.y1) * 0.1)
        add_x = int((box.x2 - box.x1) * 0.1)

        img_crop = img[max(0, box.y1_int-add_y):min(box.y2_int+add_y, h),
                       max(box.x1_int-add_x, 0): min(box.x2_int+add_x, w), :]
        cv2.imwrite(image_paths[i] + '_crop_' + str(n) + '.jpg', img_crop)

    os.remove(image_paths[i])
    os.remove(label_paths[i])
