## 1. Dataset von OpenImages herunter laden
Mit dem [OIDv4_ToolKit](https://github.com/EscVM/OIDv4_ToolKit) können alle in [OpenImages](https://storage.googleapis.com/openimages/2018_04/bbox_labels_600_hierarchy_visualizer/circle.html) vorhandenen Klasses heruntergeladen werden.
Dafür die gewünschten Klassen entweder Komma getrennt oder in einem Text File demm --classes Argument übergeben.

```python
python3 main.py downloader --Dataset Dataset_Folder/ --classes classes.txt --limit 2000 --type_csv all
```
'Dataset_Folder' muss in Ordner OID zusammen mit einem Ordner csv_folder liegen.  

in csv_folder muss die Dateien [train-annotations-bbox.csv](https://storage.googleapis.com/openimages/2018_04/train/train-annotations-bbox.csv), [test-annotations-bbox.csv](https://storage.googleapis.com/openimages/2018_04/test/test-annotations-bbox.csv), [validation-annotations-bbox.csv](https://storage.googleapis.com/openimages/2018_04/validation/validation-annotations-bbox.csv) und [class-descriptions-boxable.csv](https://storage.googleapis.com/openimages/2018_04/class-descriptions-boxable.csv) enthalten.

Da Klassen Namen in den Label Files keine Leezeichen habe dürfen sollten diese durch '_' ersetzt werden.  
Dafür kann folgendes Script verwendet werden:  
```python
python3 remove_spaces.py path/to/folder
```


