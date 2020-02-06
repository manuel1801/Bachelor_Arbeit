import connection
import time
import cv2
import os
import numpy as np

conn = connection.RaspyConnection()
conn.start_client('10.42.0.111')
# conn.start_client()

workspace_dir = os.path.join(os.environ['HOME'], 'object_detection_ncs2')


assert os.path.isdir(workspace_dir)
image_name = ''
image = np.zeros((480, 640, 3))


while True:
    for msg in conn.receive_data():

        if type(msg) == str:
            image_name = msg
            print('msg receive: ', image_name)
        else:
            if 'detected_' in image_name:
                cv2.imwrite(os.path.join(workspace_dir,
                                         'detected', image_name + '.png'), msg)
            elif 'current_' in image_name:
                cv2.imwrite(os.path.join(workspace_dir,
                                         'current', image_name + '.png'), msg)
            else:
                cv2.imwrite(os.path.join(workspace_dir,
                                         'captures', image_name + '.png'), msg)

            image = msg

    cv2.imshow('image', image)
    cv2.waitKey(1)

    time.sleep(1)

cv2.destroyAllWindows()
conn.end_connection()
