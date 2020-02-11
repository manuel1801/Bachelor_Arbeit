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

Auf [remot3.it](https://remote.it/) registrieren oder einloggen:


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





### b) Sockt über Tcp

## Mobiles Internet

### Huawei E3531 SurfStick

[Huawei E3531 SurfStick](https://www.amazon.de/gp/product/B00HSZEY34/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
am Rasperry [einrichten](https://tutorials-raspberrypi.de/raspberry-pi-gsm-modul-mobiles-internet/) 

