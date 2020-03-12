

# Applikation

Zur Ausführung den *Application* Ordner mit Folgendem
Inhalt auf den Raspberry Pi kopieren:

oder nur den *Application* Ordner mit folgendem Inhalt:

```bash

└── Application/
    ├── models/
    │   └── animals_faster_rcnn_inception/
    │       ├── frozen_inference_graph.xml
    │       └── ...
    ├── launcher.sh
    ├── detection.py
    └── connection.py
```



## Einstellungen

Folgende Variablen müssen definiert werden:

* Senden der Daten

```python
send_results = True # ob die Bilder an ein remote Gerät gesendet werden sollen. (bei False werden die Bilder lokal abgespeichert) 
send_email = '' # E-Mail adresse (nur wenn send_results=True) an die zusätzlich eine Benachrichtigung per E-Mail gesendet werden soll (oder None wenn nicht)
```

* Geräte Namen

```python
user = 'pi'             # user name des Raspeberry Pi

# nur wenn gesendet werden soll
remote_user = ''        # name des Gerätes (PC) an das gesendet werden soll
remote_divice_name = '' # name des Gerätes in remote.it
```

* Passwörter (nur wenn Daten gesendet werden sollen)

```python
password_remote_divece = '' # passwort des Gerätes (PC) an das gesendet werden soll
password_remoteit = ''      # passwort des remote.it accounts (auc)
```

* weitere Einstellungen (optional, default wert kann beibehalten werden)
```python
buffer_size = 200       # Anzahl der Frames die zwischengespeichert werden können
threshhold = 0.7        # Threshold, nach denen anhand der Wahrschienlichkeit die erkannten objekte gefiltert werden
num_requests = 3        # anzahl paralleler inferenz requests
n_save = 10             # nach wie vielen Erkannten Tieren (der gleichen Klasse) gespeicher und gesendet werden soll
```

## Ausführung


## Autostart







```python
password = '*****'      # von remote.it account und remote gerät
raspi = True            # ob auf

buffer_size = 200    # zum zwischen speichern wenn infer langsamer stream
threshhold = 0.5     # Für Detections
num_requests = 2     # anzahl paralleler inferenz requests, recommended:3
send_results = False  # falls nein wird local gespeichert)
# None: keine email sende, oder in send_mail zieladresse angeben.
send_email = None
send_all_every = 100  # wie oft alle detections senden (in sekunden, 0 für nie)

# nach wie vielen detections einer klasse save and send
# n_save = 300       # für SSDs mit ca 30 FPS
n_save = 5        # 10 für Faster R-CNNs mit ca 0,7 FPS
```


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

