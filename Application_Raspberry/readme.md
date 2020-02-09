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


### b) Sockt über Tcp