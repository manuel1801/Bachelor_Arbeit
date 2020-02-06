#!/usr/bin/python

# https://github.com/sabjorn/NumpySocket
# https://stackoverflow.com/questions/20820602/image-send-via-tcp

import socket
import cv2
import numpy as np


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


class MySocket:
    def __init__(self):
        self.address = 0
        self.port = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.type = None

    def start_server(self, address='10.10.73.89', port=5001):
        self.type = 'server'
        self.address = address
        self.port = port
        self.socket.bind((self.address, self.port))
        self.socket.listen(True)
        self.sever_conn, self.server_addr = self.socket.accept()

    def receive_image(self):

        if self.type is not 'server':
            print('not set up as server')
            return 0

        self.length = recvall(self.sever_conn, 16)
        self.stringData = recvall(self.sever_conn, int(self.length))

        self.data = np.fromstring(self.stringData, dtype='uint8')
        self.img = cv2.imdecode(self.data, 1)
        return self.img

    def receive_text(self):
        if self.type is not 'server':
            print('not set up as server')
            return 0
        self.text = self.sever_conn.recv(1024)
        return self.text

    def receive_ok(self):
        if self.type is not 'server':
            print('not set up as server')
            return 0
        self.sever_conn.send('ok'.encode('utf-8'))

    def end_server(self):
        self.sever_conn.shutdown(1)
        self.sever_conn.close()

    def start_client(self, address='10.10.73.89', port=5001):
        self.type = 'client'
        self.address = address
        self.port = port
        self.socket.connect((self.address, self.port))

    def send_image(self, img):
        if self.type is not 'client':
            print('not set up as client')
            return 0

        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.result, self.imgencode = cv2.imencode(
            '.jpg', img, self.encode_param)

        self.data = np.array(self.imgencode)
        self.stringData = self.data.tostring()

        self.socket.send(str(len(self.stringData)).ljust(16).encode('utf-8'))
        self.socket.send(self.stringData)

        self.socket.recv(20)

    def send_text(self, msg):
        if self.type is not 'client':
            print('not set up as client')
            return 0
        self.socket.send(msg.encode('utf-8'))
        self.socket.recv(20)

    def end_client(self):
        self.socket.shutdown(1)
        self.socket.close()
