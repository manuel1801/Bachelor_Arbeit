import paramiko
from scp import SCPClient
import cv2
from io import BytesIO
import os
import subprocess


img = 'test.jpg'
user_src = 'manuel'
user_dest = 'pi'

password = 'hiworld'

server = 'proxy50.rt3.io'
port = '36270'


src_path = os.path.join(
    '/home', user_src, 'Bachelor_Arbeit/Connection/remote_it', img)

dest_path = os.path.join(
    '/home', user_dest, 'Bachelor_Arbeit/Connection/remote_it/received', img)


try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user_dest, password)
    with SCPClient(client.get_transport()) as scp:
        scp.put(src_path, dest_path)
    print('failed with python... trying with bash')
except:
    #subprocess.Popen(['scp', ])
    os.system('scp -P 38564 test.jpg manuel@proxy55.rt3.io:/home/manuel/Bachelor_Arbeit/Connection/remote_it/received')
