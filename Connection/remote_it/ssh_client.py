import paramiko
from scp import SCPClient
import cv2
from io import BytesIO
import os

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


client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(server, port, user_dest, password)


with SCPClient(client.get_transport()) as scp:
    scp.put(src_path, dest_path)
