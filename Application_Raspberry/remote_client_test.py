import connection
from time import sleep

conn = connection.RaspyConnection()
# conn.start_client('proxy50.rt3.io', port=33983)
# # conn.start_client('10.42.0.111')
# conn.send_data('hi', 'text')
# conn.end_connection()
# exit()

conn.start_server('proxy8.remoteiot.com', port=14491)
quited = False

while True:

    for msg in conn.receive_data():
        print(msg)
        if msg == 'quit':
            quited = True
            break

    if quited:
        break

    sleep(1)

conn.end_connection()
