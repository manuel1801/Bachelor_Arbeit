
import cv2
import subprocess
import os
import sys

# python3 convert_to_grayscale.py path/to/dataset
# erzeugt copy des dataset und wandelt alle bilder in graustufen um

dataset_dir = sys.argv[1]

if dataset_dir[-1] == '/':
    dataset_dir = dataset_dir[:-1]


# create copy of full dataset
os.system('cp -r ' + dataset_dir + ' ' + dataset_dir + '_gray')

# get paths to all image files
pr = subprocess.Popen(['find', dataset_dir + '_gray', '-name', '*.jpg'],
                      stdout=subprocess.PIPE)

# collect paths in a list
image_paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]

# convert all images to grayscale
for img_path in image_paths:
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(img_path, img)
