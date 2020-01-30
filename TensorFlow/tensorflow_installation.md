# Install Tensorflow-gpu

### 1. Miniconda 

Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)


```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

### 2. Create Environment

```bash
conda create -n tf_env python=3.7
conda activate tf_env
```
### 4. Install Tensorflow-gpu
```bash
conda install -c conda-forge tensorflow-gpu==1.14
```

### 5. Check Versions

Make shure cudatoolkit, cudnn and nvidia driver fit together as shown in the [Cuda Support Matrix](https://docs.nvidia.com/deeplearning/sdk/cudnn-support-matrix/index.html).

```bash
conda list | grep cud # for cuda/cudnn versions
nvidia-smi # vor driver versin
```
If not either up/downgrade nvidia driver or cuda.

### 6. Install Packages

```bash
conda install -c conda-forge keras
conda install -c conda-forge matplotlib
```




## Install Tensorflow Object Detection Api

[Documentation/Tutorial](https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/training.html)

### 1. Tensorflow Models
Clone the tensorflow Models Repository which contains the Object Detectin Api:
```bash
git clone https://github.com/tensorflow/models.git
```

### 2. Protobuf

* Download Python Version of [Protbuf](https://github.com/google/protobuf/releases)
* install Protobuf:

```bash
sudo ./configure
sudo make check
sudo make install
sudo ldconfig
cd models/research
protoc object_detection/protos/*.proto –python_out=.
```

* Environment Variablen im .bashrc hinzufügen:
```
export PYTHONPATH=$PYTHONPATH:/path/to/TensorFlow/models/research:/path/to/TensorFlow/models/research/slim:/path/to/TensorFlow/models/research/object_detection
```
in letzte Zeile schreiben.

### 3. Tensorboard
