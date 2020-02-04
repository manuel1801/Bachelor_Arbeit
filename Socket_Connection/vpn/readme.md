## PPTP

[client](https://devtidbits.com/2013/02/19/using-a-point-to-point-tunnelling-protocol-virtual-private-network-pptp-vpn-client-on-a-raspberry-pi/)


install pptp
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y pptp-linux
```


configure via perl script
```bash
cd /usr/sbin/
sudo pptpsetup --create my_pptp_client --server de4.vpnbook.com --username vpnbook --password 3hx2rxv --start

```
gives this error

```bash
Couldn't open the /dev/ppp device: No such device or address
pppd: Please load the ppp_generic kernel module.

```



[server](https://www.linuxbabe.com/linux-server/setup-your-own-pptp-vpn-server-on-debian-ubuntu-centos)


bis 3. 3. Adding VPN User Accounts



## OpenVPN

[ubuntu server (sorce)](https://www.cyberciti.biz/faq/ubuntu-18-04-lts-set-up-openvpn-server-in-5-minutes/)

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

