import paramiko
from scp import SCPClient
import cv2
import os
import subprocess
import pexpect


user = 'manuel'

if user == 'pi':
    file = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test.jpg'
    path = '/home/pi/Bachelor_Arbeit/Connection/remote_it/received'
else:
    file = '/home/pi/Bachelor_Arbeit/Connection/remote_it/test.jpg'
    path = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/received'


password = 'hiworld'

server = 'proxy55.rt3.io'
port = '38564'


def send_with_module(server, port, user, password, file, path):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        with SCPClient(client.get_transport()) as scp:
            scp.put(file, path)
        print('succesfully send with python')
    except Exception as e:
        print(e)


def send_with_command(server, port, user, password, file, path):
    command = 'scp -P {} {} {}@{}:{}'.format(
        port,
        file,
        user,
        server,
        path
    )
    print(command)

    try:
        child = pexpect.spawn(command)
        r = child.expect(["{}@{}'s password:".format(user, server), pexpect.EOF])
        if r == 0:
            child.sendline(password)
            child.expect(pexpect.EOF)
        elif r == 1:
            print('end of file')
    except Exception as e:
        print(e)

send_with_command(server, port, user, password, file, path)
