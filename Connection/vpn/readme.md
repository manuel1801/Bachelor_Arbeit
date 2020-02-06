## PPTP

### client

[Using a Point-to-Point Tunnelling Protocol, Virtual Private Network (PPTP VPN) client on a Raspberry Pi](https://devtidbits.com/2013/02/19/using-a-point-to-point-tunnelling-protocol-virtual-private-network-pptp-vpn-client-on-a-raspberry-pi/)



### Server

[official ubuntu doc](https://help.ubuntu.com/community/PPTPServer)
oder [hier](https://www.linuxbabe.com/linux-server/setup-your-own-pptp-vpn-server-on-debian-ubuntu-centos)
oder [hier](https://adminforge.de/linux-allgemein/pptp-vpn-server-unter-debian-wheezy-einrichten/)



```bash
sudo apt-get install openvpn easy-rsa
```



```bash
sudo su
```


```bash
cp -r /usr/share/easy-rsa /etc/openvpn/easy-rsa
cd /etc/openvpn/easy-rsa
mkdir keys
```


```bash
cp openssl-1.0.0.cnf openssl.cnf

```


```bash
nano vars
```



```bash

export KEY_ALTNAMES="EasyRSA"


export KEY_CONFIG="$EASY_RSA/openssl.cnf"

export KEY_SIZE=2048


export KEY_COUNTRY="DE"
export KEY_PROVINCE="BW"
export KEY_CITY="Reutlingen"
export KEY_ORG="meineorganisation"
export KEY_EMAIL="manuel.barkey@gmail.com"
export KEY_OU="meineabteilung"



```


```bash
./clean-all
./build-ca
```
und werte (in eckigen klammern) mit enter bestätigen


```bash
./build-key-server myservername
```



```bash
./build-dh
```


```bash
cp myserver.crt myserver.key dh2048.pem /etc/openvpn/
```
get sample server config file
```bash
cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz /etc/openvpn/
gzip -d /etc/openvpn/server.conf.gz
nano server.conf
```
and edit

```bash

ca easy-rsa/keys/ca.crt   
cert easy-rsa/keys/myserver.cert
key easy-rsa/keys/myserver.key  # This file should be kept secret

dh easy-rsa/keys/dh2048.pem

push "redirect-gateway def1 bypass-dhcp"

```

ip forwarding
```bash
nano /etc/sysctl.conf
net.ipv4.ip_forward=1
sudo sysctl -p /etc/sysctl.conf
```



```bash
sudo ufw allow openvpn
```

with own interface for eth0 (check in ifconfig)
```bash
$ sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o wlo1 -j MASQUERADE

```

for permanent
```bash
*nat
:POSTROUTING ACCEPT [0:0] 
-A POSTROUTING -s 10.8.0.0/8 -o eth0 -j MASQUERADE
COMMIT
```

```bash
nano /etc/default/ufw
DEFAULT_FORWARD_POLICY="ACCEPT"
ufw reload
```
start and test server


```bash
systemctl start openvpn@myserver
systemctl is-active openvpn@myserver
```



```bash

```



```bash

```





for client
```bash
cd /etc/openvpn/easy-rsa/
source vars
./build-key myclient

```

```bash
mkdir client
cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf client/client.ovpn
```



## OpenVPN

### Server



[ubuntu server mit script](https://www.cyberciti.biz/faq/ubuntu-18-04-lts-set-up-openvpn-server-in-5-minutes/)

[ubuntu server (ohne script)]()

[ubuntu server wiki](https://wiki.ubuntuusers.de/OpenVPN/)


[ubuntu server (apt)](https://www.vpnbook.com/howto/setup-openvpn-on-ubuntu)


[client (linux)](https://openvpn.net/vpn-server-resources/how-to-connect-to-access-server-from-a-linux-computer/)

[client (raspi)](https://jankarres.de/2014/10/raspberry-pi-openvpn-vpn-client-installieren/)

[]()

[]()

[]()

## other

[free vpn vpnbook](https://www.vpnbook.com/)

[PPTP vs OpenVPN](https://www.shellfire.de/blog/pptp-vs-ipsec-vs-openvpn-sind-die-unterschiede/)


[aktuelle ip](https://whatismyipaddress.com/de/meine-ip)

[pivpn](https://github.com/pivpn/pivpn)

