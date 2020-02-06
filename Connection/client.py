#!/usr/bin/python

import socket
import select
import time
import sys
import numpy as np
import cv2

HEADER_LENGTH = 10

host = '10.10.73.89'
port = 12345

do_start = time.time()
do_intervall = 1  # sec

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
inout = [sys.stdin, client_socket]


while True:
    # print('select')

    if time.time() > do_start + do_intervall:
        print('doining something')
        do_start = time.time()

    infds, _, errfds = select.select(inout, [], inout, 0)  # wait for 1 sec

    for infd in infds:
        # SENDEN
        if infd == sys.stdin:
            line = sys.stdin.readline()
            if line:
                data = line.encode('utf-8')
                data_header = f'{len(data):<{HEADER_LENGTH}}'.encode('utf-8')
                infd.send(data_header + data)
        else:
            # EMPFANGEN
            print('receiving')
            data_header = infd.recv(
                HEADER_LENGTH)  # warum nicht infd.recv()

            if len(data_header) == 0:
                inout.remove(infd)
                continue

            data_length = int(data_header.decode('utf-8'))

            if data_length > 1000:  # image

                # count = data_length
                data = b''
                while data_length:
                    new_data = infd.recv(data_length)
                    if not new_data:
                        break
                    data += new_data
                    data_length -= len(new_data)

                data = np.fromstring(data, dtype='uint8')
                img = cv2.imdecode(data, 1)
                cv2.imwrite('img_received.jpg', img)

            else:  # text
                data = infd.recv(data_length).decode('utf-8')
                print('received data: ', data)
