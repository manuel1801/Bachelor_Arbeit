import connection_non_blocking as cnb
import time
import cv2

my_connection = cnb.RaspyConnection()
my_connection.start_server()
img = cv2.imread('deer.jpg')
print('iamge shape ', str(img.shape))


while True:

    print('try to send message')
    my_connection.send_data('hi', 'text')

    for msg in my_connection.receive_data():

        if type(msg) == str:
            if msg == 'get frame':
                my_connection.send_data('sending an image.', 'text')
                my_connection.send_data(img, 'image')

            else:
                print(msg)

    time.sleep(2)
    my_connection.send_data(img, 'image')


my_connection.end_connection()
