import pyrealsense2 as rs
import numpy as np
import cv2

# Doku: https://intelrealsense.github.io/librealsense/python_docs/index.html

# für punkte: https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/box_dimensioner_multicam/realsense_device_manager.py
# https://forums.intel.com/s/question/0D70P0000069qxHSAQ/how-to-enabledisable-emitter-through-python-wrapper-pyrealsense2?language=de


pipeline = rs.pipeline()
config = rs.config()

# config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 30)

pipeline_profile = pipeline.start(config)
device = pipeline_profile.get_device()

sensor = device.query_sensors()[0]
emitter_option = 1
sensor.set_option(rs.option.emitter_enabled, emitter_option)
# sensor.set_option(rs.option.laser_power, 50)


fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out_ir = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480), 0)
# out_color = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# t1 = cv2.getTickCount()

try:
    while True:

        frames = pipeline.wait_for_frames()

        # color_frame = frames.get_color_frame()
        ir_frame = frames.get_infrared_frame()

        # color_image = np.asanyarray(color_frame.get_data())
        ir_image = np.asanyarray(ir_frame.get_data())

        # out_color.write(color_image)
        # out_ir.write(ir_image)

        # cv2.imshow("Color Stream", color_image)
        cv2.imshow("Infrared Stream", ir_image)

        # exit on 'esc' or 'q' key
        key = cv2.waitKey(1)

        # t2 = cv2.getTickCount()
        # t = (t2 - t1) / cv2.getTickFrequency()
        # if t > 30:
        #     break

        if key == 32:  # space
            emitter_option = abs(emitter_option - 1)
            sensor.set_option(rs.option.emitter_enabled, emitter_option)

        if key == 113 or key == 27:  # q oder esc
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
