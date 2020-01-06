import os
import cv2
import numpy as np
import pyrealsense2 as rs
from openvino.inference_engine import IENetwork, IEPlugin


model = 'mobilenet-ssd'

model_xml = '/home/manuel/Bachelor_Arbeit/models/' + model + '/' + model + '.xml'
model_bin = '/home/manuel/Bachelor_Arbeit/models/' + model + '/' + model + '.bin'

LABELS = ('background',
          'aeroplane', 'bicycle', 'bird', 'boat',
          'bottle', 'bus', 'car', 'cat', 'chair',
          'cow', 'diningtable', 'dog', 'horse',
          'motorbike', 'person', 'pottedplant',
          'sheep', 'sofa', 'train', 'tvmonitor')

device = 'MYRIAD'


# Create Plugin
plugin = IEPlugin(device=device)

# Create Network
net = IENetwork(model=model_xml, weights=model_bin)
# Load Model into plugin
exec_net = plugin.load(network=net, num_requests=2)

# get in/ou and shapes of the network
input_blop = next(iter(net.inputs))
output_blop = next(iter(net.outputs))
n, c, h, w = net.inputs[input_blop].shape

# setup cameras
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)


# get frame from camera
pipeline.start(config)

iteration = 0
while True:

    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())

    cv2.imshow('RealSense', frame)
    cv2.waitKey(1)

    # preprocess frame
    # auf netzwerk input größe verkleinern
    image = cv2.resize(frame, (w, h))
    # von h,w,c -> nach c,h,w (network format)
    image = image.transpose((2, 0, 1))
    image = image.reshape(n, c, h, w)  # n hinzufügen

    # do the inference
    # res ist dict mit key:output_blop und value:array mit probabailty (arrInd is ClassInd)
    res = exec_net.infer(inputs={input_blop: image})

    # get output blop
    # 0 da hier nur ein bild verwendet wird (n=1)
    res = res[output_blop][0]

    # get class index and probability of highest
    top_ind = np.argsort(res)[:6]

    if iteration % 50 == 0:
        for i in top_ind:
            print(res[i])

    iteration += 1
    # write results to list
    # predicted = [labels[i].split(' ', 1)[-1] for i in top_ind]
    # probs = [res[i] for i in top_ind]
