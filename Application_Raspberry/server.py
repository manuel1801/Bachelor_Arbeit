import connection
import time
import cv2
import os
import numpy as np

conn = connection.RaspyConnection()
conn.start_server()

workspace_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/Application_Raspberry')


assert os.path.isdir(workspace_dir)
image_name = ''
image = None


while True:
    for msg in conn.receive_data():
        if type(msg) == str:
            image_name = msg
            print('msg receive: ', image_name)
        else:
            cv2.imwrite(os.path.join(workspace_dir,
                                     'detected', image_name + '.png'), msg)
            #image = msg

    # if image is not None:
    #     cv2.imshow('received', image)
    #     if cv2.waitKey(1) == 113:
    #         break
    time.sleep(1)

# cv2.destroyAllWindows()
conn.end_connection()
