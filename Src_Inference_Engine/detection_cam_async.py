
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser, SUPPRESS
import cv2
import time
import logging as log
import pyrealsense2 as rs
import numpy as np
# import connection
import datetime

# hier noch neue Socket connectin (non blocking) implementieren!!

from openvino.inference_engine import IENetwork, IECore

# dataset = 'Beispiel_Set'
# dataset = 'OI_Animals'
dataset = 'coco'

model = 'ssd_inception_v2'
# model = 'ssd_mobilenet_v2'

sock = 0

default_model = '/home/manuel/Bachelor_Arbeit/models/' + \
    dataset + '_' + model + '/frozen_inference_graph.xml'

default_model = '/home/manuel/Bachelor_Arbeit/models_deprecated/faster_rcnn_inception_v2_coco/frozen_inference_graph.xml'


if dataset == 'coco':
    coco_ind = 0
    labels_map = [l.strip().split('display_name: ')[-1] for l in open('/home/manuel/Bachelor_Arbeit/models_deprecated/' +
                                                                      dataset + '_' + model + '/classes.txt').readlines() if 'display_name:' in l]
else:
    coco_ind = -1
    labels_map = [l.strip() for l in open('/home/manuel/Bachelor_Arbeit/models/' +
                                          dataset + '_' + model + '/classes.txt').readlines()]


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help',
                      default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-m", "--model", help="Required. Path to an .xml file with a trained model.",
                      required=False, type=str, default=default_model)
    args.add_argument("-s", "--socket_conn", help="send detected fram via tcp to a host.",
                      required=False, type=int, default=sock)
    args.add_argument("-pt", "--prob_threshold", help="Optional. Probability threshold for detections filtering",
                      default=0.5, type=float)
    return parser


def main():
    log.basicConfig(format="[ %(levelname)s ] %(message)s",
                    level=log.INFO, stream=sys.stdout)
    args = build_argparser().parse_args()

    if args.socket_conn == 1:
        detected_objects = dict()
        conn = connection.MySocket()
        conn.start_client()

    model_xml = args.model
    model_bin = os.path.splitext(model_xml)[0] + ".bin"

    log.info("Creating Inference Engine...")
    ie = IECore()

    # Read IR
    log.info("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
    net = IENetwork(model=model_xml, weights=model_bin)

    img_info_input_blob = None
    feed_dict = {}
    for blob_name in net.inputs:
        if len(net.inputs[blob_name].shape) == 4:
            input_blob = blob_name
        elif len(net.inputs[blob_name].shape) == 2:
            img_info_input_blob = blob_name
        else:
            raise RuntimeError("Unsupported {}D input layer '{}'. Only 2D and 4D input layers are supported"
                               .format(len(net.inputs[blob_name].shape), blob_name))

    assert len(net.outputs) == 1, "Demo supports only single output topologies"

    out_blob = next(iter(net.outputs))
    log.info("Loading IR to the plugin...")
    exec_net = ie.load_network(
        network=net, num_requests=2, device_name='MYRIAD')
    # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    if img_info_input_blob:
        feed_dict[img_info_input_blob] = [h, w, 1]

    pipline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipline.start(config)

    cur_request_id = 0
    next_request_id = 1

    log.info("Starting inference in async mode...")
    is_async_mode = True
    render_time = 0

    frames = pipline.wait_for_frames()
    frame = frames.get_color_frame()
    frame = np.asanyarray(frame.get_data())

    print("To close the application, press 'CTRL+C' here or switch to the output window and press ESC key")
    print("To switch between sync/async modes, press TAB key in the output window")

    while True:

        frames = pipline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        if is_async_mode:
            next_frame = np.asanyarray(color_frame.get_data())
            initial_h, initial_w = next_frame.shape[:2]
        else:
            frame = np.asanyarray(color_frame.get_data())
            initial_h, initial_w = frame.shape[:2]

        # Main sync point:
        # in the truly Async mode we start the NEXT infer request, while waiting for the CURRENT to complete
        # in the regular mode we start the CURRENT request and immediately wait for it's completion
        inf_start = time.time()
        if is_async_mode:
            in_frame = cv2.resize(next_frame, (w, h))
            # Change data layout from HWC to CHW
            in_frame = in_frame.transpose((2, 0, 1))
            in_frame = in_frame.reshape((n, c, h, w))
            feed_dict[input_blob] = in_frame
            exec_net.start_async(request_id=next_request_id, inputs=feed_dict)
        else:
            in_frame = cv2.resize(frame, (w, h))
            # Change data layout from HWC to CHW
            in_frame = in_frame.transpose((2, 0, 1))
            in_frame = in_frame.reshape((n, c, h, w))
            feed_dict[input_blob] = in_frame
            exec_net.start_async(request_id=cur_request_id, inputs=feed_dict)
        if exec_net.requests[cur_request_id].wait(-1) == 0:
            inf_end = time.time()
            det_time = inf_end - inf_start

            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]
            for obj in res[0][0]:
                # Draw only objects when probability more than specified threshold
                if obj[2] > args.prob_threshold:
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    class_id = int(obj[1])
                    # Draw box and label\class_id
                    color = (min(class_id * 12.5, 255),
                             min(class_id * 7, 255), min(class_id * 5, 255))
                    cv2.rectangle(frame, (xmin, ymin),
                                  (xmax, ymax), (255, 255, 0), 2)
                    det_label = labels_map[class_id + coco_ind] if labels_map else str(
                        class_id)
                    cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 0), 1)

                    print(det_label, obj[2])

                    if args.socket_conn == 1:
                        # detected_objects -> class_id:(nr, roi, perc)
                        if not class_id in detected_objects:
                            detected_objects[class_id] = [
                                0, frame[ymin:ymax, xmin:xmax], obj[2]]
                        else:
                            detected_objects[class_id][0] += 1
                            if detected_objects[class_id][2] < obj[2]:
                                detected_objects[class_id][1] = frame[ymin:ymax, xmin:xmax]
                                detected_objects[class_id][2] = obj[2]

                        # send detected roi of current class after 100 detections
                        if detected_objects[class_id][0] > 50:
                            dt = str(datetime.datetime.now()).replace(' ', '_')
                            conn.send_text(dt + '_' + det_label)
                            conn.send_image(detected_objects[class_id][1])
                            del detected_objects[class_id]

            # Draw performance stats
            inf_time_message = "Inference time: N\A for async mode" if is_async_mode else \
                "Inference time: {:.3f} ms".format(det_time * 1000)
            render_time_message = "OpenCV rendering time: {:.3f} ms".format(
                render_time * 1000)
            async_mode_message = "Async mode is on. Processing request {}".format(cur_request_id) if is_async_mode else \
                "Async mode is off. Processing request {}".format(
                    cur_request_id)

            cv2.putText(frame, inf_time_message, (15, 15),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)
            cv2.putText(frame, render_time_message, (15, 30),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)
            cv2.putText(frame, async_mode_message, (10, int(initial_h - 20)), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (10, 10, 200), 1)

        #
        render_start = time.time()
        cv2.imshow("Detection Results", frame)
        render_end = time.time()
        render_time = render_end - render_start

        if is_async_mode:
            cur_request_id, next_request_id = next_request_id, cur_request_id
            frame = next_frame

        key = cv2.waitKey(1)
        if key == 27:
            break
        if (9 == key):
            is_async_mode = not is_async_mode
            log.info("Switched to {} mode".format(
                "async" if is_async_mode else "sync"))

    cv2.destroyAllWindows()
    if args.socket_conn == 1:
        conn.end_client()
    pipline.stop()


if __name__ == '__main__':
    sys.exit(main() or 0)
