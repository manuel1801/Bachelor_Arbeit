import detect_images as detection
import os
import cv2
import subprocess
from random import shuffle

# Directory of the Datasets
dataset_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/Dataset')

# Path to converted openvino Models
# .../Animals/<model_name>/frozen_inference_graph.xml (and .bin)
models_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/openvino_models/Animals/')

# Directory to write results into
eval_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/Inference_Engine_Tools/infer_test_images/results')


# Validation Datensatz
validation_images = os.path.join(dataset_dir, 'OI_Animals/validation')
assert os.path.isdir(validation_images)


# iWild Datensatz von Kaggle
kaggle_iWildCam = os.path.join(dataset_dir, 'kaggle_iWildCam')
assert os.path.isdir(kaggle_iWildCam)


# Eigne Bilder
handy_images = os.path.join(dataset_dir, 'handy_bilder')
assert os.path.isdir(handy_images)

handy_videos = os.path.join(dataset_dir, 'handy_videos/frames')
assert os.path.isdir(handy_videos)

handy_videos = os.path.join(dataset_dir, 'handy_videos/frames')
assert os.path.isdir(handy_videos)


# select dataset by commenting out
infer_images_list = [
    validation_images,
    kaggle_iWildCam,
    handy_images,
    handy_videos
]


def get_image_paths(imgs_dir, max_images=None):
    dataset_name = imgs_dir.split('/')[-1]
    test_images = []
    for img_dir in os.listdir(imgs_dir):
        abs_img_dir = os.path.join(imgs_dir, img_dir)
        if img_dir[-3:] == 'jpg':
            test_images.append(abs_img_dir)
        elif os.path.isdir(abs_img_dir):
            for i, sub_img_dir in enumerate(os.listdir(abs_img_dir)):
                abs_sub_img_dir = os.path.join(abs_img_dir, sub_img_dir)
                if sub_img_dir[-3:] == 'jpg':
                    test_images.append(abs_sub_img_dir)
                if max_images and i == max_images:
                    break
    return dataset_name, test_images


# key=dataset_name:value=list:paths_to_images
dataset_dict = {name: data for name, data in list(
    map(get_image_paths, infer_images_list))}

# shuffle each list of image paths
for name, data in dataset_dict.items():
    shuffle(data)

print('select dataset')
names = []
for i, name in enumerate(dataset_dict):
    print(i, name)
    names.append(name)

dataset_name = names[int(input())]
dataset_files = dataset_dict[dataset_name]

max_images = None
if len(dataset_files) > 1000:
    print('select max samples (0 for all)')
    max_images = int(input())
    if max_images < 0:
        max_images = None


print('select model')
models = []
for i, model in enumerate(os.listdir(models_dir)):
    if not os.path.isdir(os.path.join(models_dir, model)):
        continue
    print(len(models), model)
    models.append(model)
model = models[int(input())]


# create exec Model
infer_model = detection.InferenceModel()
model_dir = os.path.join(models_dir, model)
model_xml = os.path.join(model_dir, 'frozen_inference_graph.xml')
model_bin = os.path.join(model_dir, 'frozen_inference_graph.bin')


if os.path.isfile(os.path.join(model_dir, 'classes.txt')):
    labels = [l.strip() for l in open(os.path.join(
        model_dir, 'classes.txt')).readlines()]
else:
    labels = None

exec_model = infer_model.create_exec_infer_model(
    model_xml, model_bin, labels, num_requests=3)


if not os.path.isdir(eval_dir):
    os.mkdir(eval_dir)

infer_results = 'infer_results_' + dataset_name

output_dir = os.path.join(eval_dir, infer_results, model)
output_dir_all = os.path.join(eval_dir, infer_results, 'all')


if not os.path.isdir(os.path.join(eval_dir, infer_results)):
    os.mkdir(os.path.join(eval_dir, infer_results))

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

if not os.path.isdir(output_dir_all):
    os.mkdir(output_dir_all)

for ind, test_image in enumerate(dataset_files):

            # load image to infer
    image = cv2.imread(test_image)

    # infer image
    result = exec_model.infer_image(image, threshhold=0.7)
    image_name = test_image.split(
        '/')[-1][:-4] + '_' + model + '.jpg'
    image_path = os.path.join(output_dir, image_name)

    # write infered image to outputdir
    cv2.imwrite(image_path, result)

    # delete existing links
    if os.path.islink(os.path.join(output_dir_all, image_name)):
        os.remove(os.path.join(
            output_dir_all, image_name))

        # create symbolik link to infered image in 'all/'
    os.symlink(image_path, os.path.join(output_dir_all, image_name))

    if max_images and ind > max_images:
        break
