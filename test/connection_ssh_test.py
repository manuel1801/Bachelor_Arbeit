import cv2
import os
import connection_ssh as connection
from time import sleep

user = 'manuel'
password = 'animalsdetection'

if user == 'pi':
    file = '/home/manuel/Bachelor_Arbeit/test/test.jpg'
    file2 = '/home/manuel/Bachelor_Arbeit/test/test2.jpg'
    file3 = '/home/manuel/Bachelor_Arbeit/test/test3.jpg'
    path = '/home/pi/Bachelor_Arbeit/test/received/'
    my_device = 'ssh-Pi'

else:
    file = '/home/pi/Bachelor_Arbeit/test/test.jpg'
    file2 = '/home/pi/Bachelor_Arbeit/test/test2.jpg'
    file3 = '/home/pi/Bachelor_Arbeit/test/test3.jpg'
    path = '/home/manuel/Bachelor_Arbeit/test/received'
    my_device = 'ssh-Pc'


conn = connection.SSHConnect()
print('TEST: connection created')

conn.login()
print('TEST: logged in')


addr = conn.get_device_adress(device_name=my_device)
print('TEST: got address')

conn_ret = None
try:
    conn_ret = conn.connect(device_address=addr)
except:
    print('exception 1')

if conn_ret:
    print('TEST: connected sucessfully')
    print(conn_ret)
    server, port, conn_id = conn_ret
    print('sendign file 1')
    conn.send(server, port, user, password, file, path)
    conn.disconnect(addr, conn_id)

else:
    print('TEST: connected errot')


conn_ret = None
try:
    conn_ret = conn.connect(device_address=addr)
except:
    print('exception 2')

if conn_ret:
    print('TEST: connected sucessfully')
    print(conn_ret)
    server, port, conn_id = conn_ret
    print('sendign file 2')
    conn.send(server, port, user, password, file2, path)
    print('sendign file 3')
    conn.send(server, port, user, password, file3, path)
    conn.disconnect(addr, conn_id)

else:
    print('TEST: connected errot')
