import cv2
import os
import connection_ssh as connection

user = 'pi'
password = 'hiworld'
puplic_ip = '129.143.140.51'

if user == 'pi':
    file = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test.jpg'
    file2 = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test2.jpg'
    file3 = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test3.jpg'
    path = '/home/pi/Bachelor_Arbeit/Connection/remote_it/received/'
    my_device = 'ssh-Pi'

else:
    file = '/home/pi/Bachelor_Arbeit/Connection/remote_it/test.jpg'
    file2 = '/home/pi/Bachelor_Arbeit/Connection/remote_it/test2.jpg'
    file3 = '/home/pi/Bachelor_Arbeit/Connection/remote_it/test3.jpg'
    path = '/home/manuel/Bachelor_Arbeit/Connection/remote_it/received'
    my_device = 'ssh-Pc'


conn = connection.SSHConnect()
conn.login()
addr = conn.get_device_adress(device_name=my_device)

ret = conn.connect(
    device_address=addr)

if not ret:
    print('connection error')
    exit()

server, port, device_id = ret

print('connected: ', server, port, device_id)
conn.send(server, port, user, password, file=file, path=path)
print('send file1')
conn.send(server, port, user, password, file=file2, path=path)
print('send file2')
conn.disconnect(addr, device_id)
print('disconnected')

ret = conn.connect(
    device_address=addr)

if not ret:
    print('connection error')
    exit()

server, port, device_id = ret

print('connected: ', server, port, device_id)
conn.send(server, port, user, password, file=file3, path=path)
print('send file3')
conn.disconnect(addr, device_id)
print('disconnected')
