# Apllikation Raspberry

## Autostart

1. Script **launcher.sh** erstellen und

```bash
cd <workspce_dir>
source /opt/intl/openvino/bin/setupvars.sh
/usr/bin/python3 main.py
cd /
```



2. **Service** anlegen

```bash
sudo nano /lib/systemd/system/my_init.service
```
* *launcher.sh* als background prozess in *my_init.service* fesetlegen
```
[Unit]
Description=init
After=multi-user.target

[Service]
Type=idle
ExecStart=bash /path/to/launcher.sh &

[Install]
WantedBy=multi-user.target
```

* Service freigeben und daemon laden

```bash
sudo chmod 644 /lib/systemd/system/my_init.service
sudo systemctl daemon-reload
```
* start/stop
```bash
sudo systemctl start my_init.service
sudo systemctl stop my_init.service
```

* Autostart Aktivieren/Deaktivieren
    
```bash
sudo systemctl enable  myscript
sudo systemctl disable  myscript
```
* Status abfrage
```
sudo systemctl status my_init.service
```

## Connection

### a) SCP über remote SSH

#### Auf Gerät an das Daten gesendet werden sollen (hier Linux):

1. **remoteit** installieren
```bash
curl -LkO https://raw.githubusercontent.com/remoteit/installer/master/scripts/auto-install.sh
chmod +x ./auto-install.sh
sudo ./auto-install.sh
```
und auführen

```bash
sudo connectd_installer
```
mit anmeldedaten:
* email: animals.detection@gmail.com
* pw: animalsdetection

einloggen oder neuen [account](https://remote.it/) anlegen.
(dann *api key* in main.py anpassen: [Developer API Key](https://app.remote.it/#account))

2. Gerät *remote-Pc* hinzufügen
3. SSH service *ssh-Pc* anlegen
4. exit

(bei anderen namen muss in main.py angepasst werden)

#### Verbindung testen (auf Raspberry)

in /home/pi/Bachelor_Arbeit/Connection/remote_it/connection_ssh_test.py 

```python
user = ''
password = ''
```
von angemeldeten gerät angeben und Script ausführen.



### b) Sockt über Tcp

Varient aus ~/Bachelor_Arbeit/Application_Raspberry/mit_sockets/
kann verwendet werden, wenn beide im Gleichen Netzwerk sind.




## Mobiles Internet

[Huawei E3531 SurfStick](https://www.amazon.de/gp/product/B00HSZEY34/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)


1. prüfen ob stick erkannt wird:
```bash
lsudb
```
ausgabe:
```
Bus 001 Device 004: ID 12d1:14dc Huawei Technologies Co., Ltd. E33372 LTE/UMTS/GSM HiLink Modem/Networkcard
```

2. Browser öffnen und auf 129.168.8.1 gehen

3. Pin eingeben (Pin prüfung deaktivieren)

