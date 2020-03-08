# Apllikation Raspberry

## Autostart

1. Script **launcher.sh** erstellen und

```bash
cd <workspce_dir>
source /opt/intl/openvino/bin/setupvars.sh
/usr/bin/python3 -u main.py
cd /
```
(mit -u werden ausgaben von main.py in status von service angezeigt)



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
User=pi
Group=pi
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

als standart Verbindung fenstlegen, da sonst verbindungswechsel
stattfinden kann und dann connection script evtl nicht mehr läuft.


```bash
route -n # aktuelle metrik rausfinden
```
```bash
ifmetric eth1 100 # niedriger als die anderen für höhere proi
```

für permant:  
in
```bash
sudo nano /etc/dhcpcd.conf
```
hinzufügen:


```bash
interface eth1
metric 200 # niedrigste
static ip_address=192.168.8.1
```

