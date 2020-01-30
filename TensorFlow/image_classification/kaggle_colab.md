## How to use Kaggle in Google Colab

summary of [this](https://medium.com/@opalkabert/downloading-kaggle-datasets-into-google-colab-fb9654c94235):


```bash
!pip install -U -q kaggle
!mkdir -p ~/.kaggle
```

create API Token: Kaggle→MyAccount→create API Token → kaggle.json

```
from google.colab import files
files.upload()
```
kaggle.json auswählen
copy file to created folder
```
!cp kaggle.json ~/.kaggle/
```
list existing datasets: 
```
!kaggle datasets list
```
download dataset from kaggle mit kaggle API
```
!kaggle datasets download -d cfpb/us-consumer-finance-complaints
!ls
```

