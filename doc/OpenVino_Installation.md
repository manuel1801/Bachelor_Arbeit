# Installation
## Open Vino

### 1. download OpenVino from [here](https://registrationcenter.intel.com/en/products/postregistration/?sn=CNP6-46RR8MT7&EmailID=mbarkey55%40gmail.com&Sequence=2579436&dnld=t) and extract


```bash
cd ~/Downloads
tar -xvzf l_openvino_toolkit_p_<version>.tgz
```


### 2. install OpenVino and Dependencies
```bash
cd l_openvino_toolkit_p_<version>
sudo ./isntall_GUI.sh
cd /opt/intel/openvino/install_dependencies
sudo -E ./install_openvino_dependencies.sh
```
### 3. set environment variables (for permanent in add in ~/.bashrc file)
```bash
source /opt/intel/openvino/bin/setupvars.sh
```
### 4. install model optimizers for all farmeworks
```bash
cd /opt/intel/openvino/deployment_tools/model_optimizer/install_prerequisites
sudo ./install_prerequisites.sh
```
### 5. Set up NCS2
```bash
sudo usermod -a -G users "$(whoami)"
sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo ldconfig
sudo reboot
```

### 6. run sample application
```bash
cd /opt/intel/openvino/deployment_tools/demo
./demo_squeezenet_download_convert_run.sh -d MYRIAD
```
and
```bash
./demo_security_barrier_camera.sh -d MYRIAD
```

## Raspberry Os

### 1. Download
* Rasbian Os [here](https://www.raspberrypi.org/downloads/raspbian/)
* BalenaEtcher [here](https://www.balena.io/etcher/)

### 2. Create Boot SD Card

insert sd cart to pc, start etcher, selct downloaded rasbian img and sdcard, flash sd card.  
Than add an ssh file in the boot dir of the sd card:

```bash
cd media/<user>/boot
touch ssh
```
### 3. Create new Ethernet Connection
```bash
nm-connection-editor
```
new ethernet named link-local,
IPv4Settings &rarr; Method: Shared to other computers

### 4. Connect Pi with Pc

insert sd card into the Raspberry  
connect the Raspberry to Pc via Ethernet Cable

Connct to the Raspberry with:
```bash
ssh pi@raspberrypi.local
```
and enter password: raspberry

### 5. Use Mouse and Keyboard of Laptop
### 6. Save and restore Backup
Backup
```bash
sudo dd if=/dev/mmcblk0 of=~/sd_card_backup.img # ohne p1
```
 Restore
```bash
sudo umount /dev/mmcblk0p1 # mit p1
sudo bb bs=4M if=~/ sd_card_backup.img of=~/mmcblk0
sudo sync
```


## Open Vino on Raspberry

Install [OpenVino](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html) and [OpenCV](https://software.intel.com/en-us/articles/raspberry-pi-4-and-intel-neural-compute-stick-2-setup)


## Realsense SDK on Raspberry

1. install cmake
```bash
sueo apt-get install cmake
```

2. install Realsense SDK as described [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md?source=post_page-----882933271f3d----------------------)

Anmerkungen:

* Wenn in **Install packages** fehler wie *Unable to locate package libdrm-amdgpu1-dbg* auftreten ignorieren.  
* Bei **install protobuf** anstatt *v3.5.1* Version *v3.10.1* verwenden.

