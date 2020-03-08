# SSH Connection

Verwendet [remote.it](https://remote.it/) zum senden von 
Daten mit scp über proxy ssh Verbindung.


## 1. Remote.it installieren

Auf dem Remote Gerät (an dass Daten gesendet werden sollen)

installieren

```bash
curl -LkO https://raw.githubusercontent.com/remoteit/installer/master/scripts/auto-install.sh
chmod +x ./auto-install.sh
sudo ./auto-install.sh
```
und auführen

```bash
sudo connectd_installer
```

Mit remote.it Konto anmelden, 
oder neuen [account](https://remote.it/) erstellen.  
Dann neues Gerät (z.B. *remote-Pc*) mit SSH Service (z.B. *ssh-Pc*) anlegen


## 2. Verwendung

In [*ssh_connection.py*](ssh_connection.py)

* in init(): [Developer API Key](https://app.remote.it/#account) anpassen
* in main():
    * *email* von remote.it
    * *password* von remote.it und remote gerät
    * *raspi* (true/false) (bezieht sich auf gerät das sendet!)
    * *remote_user* username des remote geräts 
    * *remote_divice_name* mit dem gerät über *connectd* angemeldet wurde
    * *file_path* datei die gesendet werden soll
    * *remote_output_dir* directory auf zielgerät


einloggen und verbinden:
```python
conn = SSHConnect(email, password)
logged_in = conn.login(remote_divice_name)
if logged_in:
    ret = conn.connect()
```
wenn erfolgreich, enthällt ret *server* und *port*, sonst false

senden
```python
server, port = ret
conn.send(server, port, remote_user, password,
        file_path, remote_output_dir)
```

verbindung trennen
```python
conn.disconnect()
```


script ausführen
```bash
python3 ssh_connection.py
```










# Socket Connection

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
* datatypes: 'image', 'text'
*  sender_sockets = select(socket_list)
* for each sender_sockets:
    * send image
    * send text

### end_connection
* socket.shutdown
* socket.close

# Email Connection