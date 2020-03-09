


# Applikation Raspberry

Zur Ausführung auf dem Raspberry Pi entweder 
gesammetes Repository in home Verzeichnis clonen:
```bash
git clone https://github.com/manuel1801/Bachelor_Arbeit.git
```
oder nur den *Application* Ordner mit folgendem Inhalt:

```bash
└── home/pi
    └── Bachelor_Arbeit/Application
        ├── models
        │   └── ...
        ├── main.py
        ├── launcher.sh
        ├── detection.py
        └── connection.py
```

## [Main-Script](main.py)

## [Detection](detection.py)

## [Verbindung](connection.py)

## [Autostart](launcher.sh)

Shell Script [launcher.sh](launcher.sh)
startet [main.py](main.py) bei Boot automatisch.  
Dafür folgenden Service auf dem Raspberry Pi anlegen:

```bash
sudo nano /lib/systemd/system/my_init.service
```

und folgendes schreiben:
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
Zugriffsrechte geben:
```bash
sudo chmod 644 /lib/systemd/system/my_init.service
```
Daemon neu laden (nach jeder änderung)
```bash
sudo systemctl daemon-reload
```

manuelles starten/stoppen des Service
```bash
sudo systemctl start my_init.service
sudo systemctl stop my_init.service
```

automatisches starten beim Boot aktivieren/deaktivieren    
```bash
sudo systemctl enable  myscript
sudo systemctl disable  myscript
```

Status abfragen (gibt Konsolenausgabe von main script aus)
```
sudo systemctl status my_init.service
```


## [Modelle](models/)
enthällt openvino modelle für *Animals* 
und *Samples*, jeweils mit SSD Inception und 
Faster R-CNN Inception trainiert.


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



# Mobiles Internet

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

