import connection_non_blocking as cnb
import time
import cv2

my_connection = cnb.RaspyConnection()
my_connection.start_client()

while True:
    print('try to send')
    my_connection.send_data('hi', 'text')
    print('try to rec')

    for msg in my_connection.receive_data():

        if type(msg) == str:
            print(msg)
        else:
            print(type(msg))
            print(msg.shape)
            cv2.imwrite('test/received_image.jpg', msg)
            my_connection.send_data('image received', 'text')
    time.sleep(3)


my_connection.end_connection()
