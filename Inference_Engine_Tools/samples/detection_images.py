from openvino.inference_engine import IENetwork, IEPlugin, IECore
import os
import cv2
import time
import pyrealsense2 as rs
import numpy as np
from random import shuffle

workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit')
models_dir = os.path.join(workspace_dir, 'openvino_models')


test_images_dir = os.path.join(workspace_dir, 'Dataset/handy_bilder/rgb')


print('select model')
selected_model = {}
i = 1
for dataset in os.listdir(models_dir):
    dataset_dir = os.path.join(models_dir, dataset)
    if os.path.isdir(dataset_dir):
        for model in os.listdir(dataset_dir):
            model_dir = os.path.join(dataset_dir, model)
            if os.path.isdir(model_dir):
                selected_model[i] = dataset, model
                print(i, dataset, model)
                i += 1

model_ind = int(input())
print(selected_model[model_ind], ' selected')

model_xml = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.xml')
model_bin = os.path.join(
    models_dir, selected_model[model_ind][0], selected_model[model_ind][1], 'frozen_inference_graph.bin')


if os.path.isfile(os.path.join(models_dir, selected_model[model_ind][0], 'classes.txt')):
    labels = [l.strip() for l in open(os.path.join(
        models_dir, selected_model[model_ind][0], 'classes.txt')).readlines()]
else:
    labels = None


assert os.path.isfile(model_bin)
assert os.path.isfile(model_xml)
assert os.path.isdir(test_images_dir)


# create the infer net
ie = IECore()
net = IENetwork(model=model_xml, weights=model_bin)
exec_net = ie.load_network(network=net, device_name='MYRIAD')

# get i/o layers names
iter_net = iter(net.inputs)
input_blop = next(iter(iter_net))
if len(net.inputs[input_blop].shape) != 4:
    print('second input used')
    input_blop = next(iter(iter_net))

output_blop = next(iter(net.outputs))

# get input shape of the model
n, c, h, w = net.inputs[input_blop].shape

# collect images
if os.path.isdir(test_images_dir):
    images = [
        os.path.join(test_images_dir, img) for img in os.listdir(test_images_dir) if img[-3:] == 'jpg']
    print(str(len(images)) + ' images found')
    shuffle(images)
elif os.path.isfile(test_images_dir) and test_images_dir[-3:] == 'jpg':
    print('one image found')
    images = [test_images_dir]
else:
    print('wrong input')
    exit()


for img_path in images:

    # load the image
    image = cv2.imread(img_path)
    img_height, img_width = image.shape[:2]

    inf_start = time.time()

    # preprocess image
    processed_img = cv2.resize(image, (w, h))  # h w c
    processed_img = processed_img.transpose((2, 0, 1))  # c h w
    processed_img = processed_img.reshape(n, c, h, w)  # n c h w

    # run inference
    res = exec_net.infer(inputs={input_blop: processed_img})
    inf_time = time.time() - inf_start

    # go through all detection results
    detection_out_key = list(res.keys())[0]
    for pred in res[list(res.keys())[0]][0][0]:
        if pred[2] < 0.5:
            continue

        # preictin class
        if labels != None:
            class_label = labels[int(pred[1]) - 1]
        else:
            class_label = int(pred[1])

        # prediction probability
        probability = round(pred[2] * 100, 3)

        label_txt = str(class_label) + ': ' + str(probability) + '%'
        print(label_txt + ' inference time: ' + str(inf_time))

        # bounding box
        xmin = np.int(pred[3] * img_width)
        ymin = np.int(pred[4] * img_height)
        xmax = np.int(pred[5] * img_width)
        ymax = np.int(pred[6] * img_height)

        cv2.rectangle(image, (xmin, ymin),
                      (xmax, ymax), color=(0, 255, 255), thickness=3)
        cv2.putText(image, label_txt, (xmin, ymin - 7), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                    color=(255, 255, 255), thickness=1)

    # resize img to h=800, w=keep ratio
    ratio = 800 / float(img_height)
    dim = (int(img_width * ratio), 800)
    image = cv2.resize(image, dim)

    # output the image with bbox
    cv2.imshow('Detection', image)

    if cv2.waitKey(0) == 113:
        break
