# Client-Server-Connection

## Class RaspyConnection
## Methods

### init()
* addr
* port
* socket

### start_server(addr, port)
* socket.bind(addr, port)
* listen = true
* socket_list [socket]

### start_client(addr, port)
* socket.connetct(addr, port)
* socket_list [stdin, socket]

### receive_data()
* notified_sockets = select(socket_list)
* for each notified_socket:
    * if: new client? add.
    * else if: stdin? send(input)
    * else: notified_socket.recv()
        * image
        * test
* **return** received data list
 
### send_data(data, datatype)
*  sender_sockets = select(socket_list)
* for each sender_sockets:
    * send image
    * send text

### end_connection
* socket.shutdown
* socket.close