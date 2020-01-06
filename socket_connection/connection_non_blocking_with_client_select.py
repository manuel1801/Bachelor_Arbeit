import socket
import select
import time
import sys
import numpy as np
import cv2


class RaspyConnection:
    def __init__(self):
        self.address = 0
        self.port = 0
        self.HEADER_LENGTH = 10  # in header noch data_type
        # self.HEADER_LENGTH = 30  # für adr, datatype, länge der nutzdaten jeweils 10
        # beim erhalten von nachricht 3x recv(HEADELEN/3) abfragen
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.type = None

    def start_server(self, address='10.10.73.89', port=5001):
        self.type = 'server'
        self.address = address
        self.port = port
        self.my_socket.bind((self.address, self.port))
        self.my_socket.listen(True)
        self.socket_list = [self.my_socket]
        self.clients = {}

    def start_client(self, address='10.10.73.89', port=5001):
        self.type = 'client'
        self.address = address
        self.port = port
        self.my_socket.connect((self.address, self.port))
        self.socket_list = [sys.stdin, self.my_socket]

    def receive_data(self):
        self.notified_sockets, _, _ = select.select(
            self.socket_list, [], [], 0)

        self.datas = []

        for notified_socket in self.notified_sockets:

            if notified_socket == self.my_socket and self.type == 'server':
                # add new client
                # client zusammen mit clien adr in dict clients speichern
                self.client_socket, self.client_adress = notified_socket.accept()
                self.clients[self.client_socket] = self.client_adress
                # bei senden auf anfrage den client nach adr aus dict auswählen.
                # beim senden muss adr in header mit versendet werden. receive_data returnt dann dict mit data und zugehörigem client
                # send funktion bekomomt zweites arg mit liste aus clients an die gesendet werden soll (wenn nicht angegeben bradcast)
                self.socket_list.append(self.client_socket)
                print('client connected')

            elif notified_socket == sys.stdin and self.type == 'client':
                # Receive from stdin and send
                self.line = sys.stdin.readline()
                if self.line:
                    self.data = self.line.encode('utf-8')
                    self.data_header = f'{len(self.data):<{self.HEADER_LENGTH}}'.encode(
                        'utf-8')
                    self.my_socket.send(self.data_header + self.data)

            else:
                # Receive
                self.data_header = notified_socket.recv(self.HEADER_LENGTH)
                if len(self.data_header) == 0:
                    self.socket_list.remove(notified_socket)
                    continue
                self.data_length = int(self.data_header.decode('utf-8'))
                if self.data_length > 1000:  # hier mit data type im header arbeiten
                    # receive image
                    self.data = b''
                    while self.data_length:
                        self.new_data = notified_socket.recv(
                            self.data_length)
                        if not self.new_data:
                            break
                        self.data += self.new_data
                        self.data_length -= len(self.new_data)

                    self.data = np.fromstring(self.data, dtype='uint8')
                    self.datas.append(cv2.imdecode(self.data, 1))
                else:

                    # receive text
                    self.data = notified_socket.recv(
                        self.data_length).decode('utf-8').strip()

                    if self.type == 'server':  # wenn server: adr von client der gesendet hat mit zurück geben
                        self.data = [self.data, self.clients[notified_socket]]

                    self.datas.append(self.data)
                    print('data received')

        return self.datas

    # nur von server verwendet
    # arg: list of sockets and die gesendet werden soll
    def send_data(self, data, data_type, dest_adress=None):
        _, self.sender_sockets, _ = select.select([], self.socket_list, [], 0)
        for sender_socket in self.sender_sockets:
            if sender_socket == sys.stdin:
                continue
            if dest_adress == None or clients[sender_socket] in dest_adress:
                if data_type == 'image':
                    self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                    _, self.img_encode = cv2.imencode(
                        '.jpg', data, self.encode_param)
                    # tostring erzugt bytes
                    self.img_string = np.array(self.img_encode).tostring()
                    self.img_header = f'{len(self.img_string):<{self.HEADER_LENGTH}}'.encode(
                        'utf-8')
                    sender_socket.send(self.img_header + self.img_string)
                elif data_type == 'text':
                    self.data = data.encode('utf-8')
                    self.data_header = f'{len(self.data):<{self.HEADER_LENGTH}}'.encode(
                        'utf-8')
                    sender_socket.send(self.data_header + self.data)

    def end_connection(self):
        self.my_socket.shutdown(1)
        self.my_socket.close()
