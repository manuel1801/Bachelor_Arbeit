from openvino.inference_engine import IENetwork, IECore
import os
from time import time
import cv2


use_import = True
do_export = True


workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit')

model_dir = os.path.join(
    workspace_dir, 'openvino_models/Animals/faster_rcnn_inception_v2_l2')


# model_dir = os.path.join(
#     workspace_dir, 'openvino_models/Animals/ssd_inception_v2')


model_xml = os.path.join(
    model_dir,  'frozen_inference_graph.xml')
model_bin = os.path.join(
    model_dir,  'frozen_inference_graph.bin')


ie = IECore()

net = IENetwork(model_xml, model_bin)

test_images = os.path.join(workspace_dir, 'Dataset/handy_bilder/images')
test_images = [os.path.join(test_images, test_image)
               for test_image in os.listdir(test_images)]


labels = ['Brown_bear',
          'Deer',
          'Fox',
          'Goat',
          'Hedgehog',
          'Owl',
          'Rabbit',
          'Raccoon',
          'Squirrel']


if use_import:
    t_start = time()
    exec_net = ie.import_network(model_file=os.path.join(
        model_dir, 'exported_model'), device_name='MYRIAD')
    print('model import time' + str(time() - t_start))

else:
    t_start = time()
    exec_net = ie.load_network(net, num_requests=2, device_name='MYRIAD')
    print('model loading time: ' + str(time() - t_start))

    if do_export:
        exec_net.export(os.path.join(
            model_dir, 'exported_model'))


feed_dict = {}
img_info_input_blob = None
for blob_name in net.inputs:
    if len(net.inputs[blob_name].shape) == 4:
        input_blob = blob_name
    elif len(net.inputs[blob_name].shape) == 2:
        img_info_input_blob = blob_name
    else:
        print('error!')

assert len(
    net.outputs) == 1, "Demo supports only single output topologies"


out_blob = next(iter(net.outputs))

n, c, h, w = net.inputs[input_blob].shape
if img_info_input_blob:
    feed_dict[img_info_input_blob] = [h, w, 1]

for n, image_path in enumerate(test_images):
    image = cv2.imread(image_path)
    img_h, img_w = image.shape[:2]
    in_frame = cv2.resize(image, (w, h))
    in_frame = in_frame.transpose((2, 0, 1))
    in_frame = in_frame.reshape((n, c, h, w))

    feed_dict[input_blob] = in_frame

    exec_net.start_async(0, feed_dict)

    if exec_net.requests[0].wait(-1) == 0:
        res = exec_net.requests[0].outputs[out_blob]

        for obj in res[0][0]:
            if obj[2] > 0.6:
                xmin = int(obj[3] * img_w)
                ymin = int(obj[4] * img_h)
                xmax = int(obj[5] * img_w)
                ymax = int(obj[6] * img_h)

                class_name = labels[int(obj[1]) - 1]

                cv2.rectangle(image, (xmin, ymin),
                              (xmax, ymax), (0, 255, 255), 2)

                cv2.putText(image, (class_name + ': ' + str(round(obj[2] * 100, 1)) + '%'),
                            (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 1)

    try:
        cv2.imshow('infer result', image)
        if cv2.waitKey(0) == 113:
            break
    except:
        print(str(n), 'imges infered')
