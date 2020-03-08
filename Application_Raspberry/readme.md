# OpenVino Installationen

## Ubuntu

### 1. [OpenVino](https://registrationcenter.intel.com/en/products/postregistration/?sn=CNP6-46RR8MT7&EmailID=mbarkey55%40gmail.com&Sequence=2579436&dnld=t) herunterladen und entpacken


```bash
cd ~/Downloads
tar -xvzf l_openvino_toolkit_p_<version>.tgz
```

### 2. OpenVino und dependencies installieren
```bash
cd l_openvino_toolkit_p_<version>
sudo ./isntall_GUI.sh
cd /opt/intel/openvino/install_dependencies
sudo -E ./install_openvino_dependencies.sh
```

### 3. Environment Variablen setze
```bash
source /opt/intel/openvino/bin/setupvars.sh
```
(in .bashrc hinzufügen für permanent)


### 4. ModelOptimizer installieren
```bash
cd /opt/intel/openvino/deployment_tools/model_optimizer/install_prerequisites
sudo ./install_prerequisites.sh
```

### 5. NCS2 einrichten
```bash
sudo usermod -a -G users "$(whoami)"
sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo ldconfig
sudo reboot
```


## Raspberry Pi

### 1. Raspberry Pi Setup

[Rasbian](https://www.raspberrypi.org/downloads/raspbian/) herunterladen und img sd karte mit 
zb [BalenaEtcher](https://www.balena.io/etcher/)
erstellen.

Dann ssh datei auf sd karte anlegen:
```bash
cd media/<user>/boot
touch ssh
```

SD Karte in Raspberry und Verbindung über Ethernet 
Kabel herstellen.  
Dann:

```bash
ssh pi@raspberrypi.local
```
passwort: *raspberry* eingeben.

### 2. OpenVino auf Raspberry Pi

[OpenVino](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html) und [OpenCV](https://software.intel.com/en-us/articles/raspberry-pi-4-and-intel-neural-compute-stick-2-setup)
installieren.





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

