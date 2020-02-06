#!/usr/bin/python

import socket
import select
import time
import numpy as np
import cv2

HEADER_LENGTH = 10

img = cv2.imread('deer.jpg')


t_start = time.time()
send_intervall = 5  # sec

do_start = time.time()
do_intervall = 1  # sec


host = '10.10.73.89'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

img_sent = False

server_socket.bind((host, port))
server_socket.listen(5)
inputs = [server_socket]


while True:

    if time.time() > do_start + do_intervall:
        print('doining something')
        do_start = time.time()

    infds, _, errfds = select.select(inputs, [], inputs, 0)

    for fds in infds:
        if fds == server_socket:  # neuer client

            print('connected to client')

            client_sock, client_addr = fds.accept()  # connection akzeptieren
            inputs.append(client_sock)  # client der lister hinzufügen

        else:
            # EMPFANGEN

            data_header = fds.recv(HEADER_LENGTH)
            if len(data_header) == 0:  # client disconnected
                inputs.remove(fds)
                continue

            data_length = int(data_header.decode('utf-8'))
            data = fds.recv(data_length).decode('utf-8')
            print('received from client: ', data)

    if time.time() > t_start + send_intervall:

        _, outfds, errfds = select.select([], inputs, inputs, 0)

        for out in outfds:

            print('sending')

            if img_sent:

                data = 'something text from the server'.encode('utf-8')
                data_header = f'{len(data):<{HEADER_LENGTH}}'.encode(
                    'utf-8')

                out.send(data_header + data)

                # t_start = time.time()

            else:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                _, img_encode = cv2.imencode('.jpg', img, encode_param)
                # tostring erzugt bytes
                img_string = np.array(img_encode).tostring()
                img_header = f'{len(img_string):<{HEADER_LENGTH}}'.encode(
                    'utf-8')
                out.send(img_header + img_string)
                img_sent = True

        t_start = time.time()
