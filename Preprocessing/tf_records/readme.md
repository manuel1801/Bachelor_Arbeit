# TF Record Files aus OpenImages Datensatu erstellen

OpenImages Datenset mit Ordnerstruktur:

```bash
└── DATASET_DIR
    ├── train
    │   ├── class1
    │   │   ├── Label
    │   │   │   ├── img1.txt
    │   │   │   └── ...
    │   │   ├── img1.jpg
    │   │   ├── img2.jpg
    │   │   └── ...
    │   └── class2
    ├── test
    │   └── class1
    └── validation
```

## 1. Bilder aus Unterordnern in test/train/validation Ordner schreiben

Bilder aus den jeweiligen klassen-unterordnern in parent train- bzw. test Ordner verschieben. (validation nicht)

mit:
```bash
./collect_files.sh path/to/DATASET_DIR
```

ergibt:
```bash
└── DATASET_DIR
    ├── train
    │   ├── labels
    │   │   └── img1.txt
    │   ├── img1.jpg
    │   └── ...
    └── test
```


## 2 OpenImages zu Pascal VOC konvertieren

Labelfiles von open image (txt) format ins pascal voc (xml) annotation 
format konvertieren.

```bash
python3 oi_to_pascal_voc_xml.py --dataset_path path/to/DATASET_DIR/
```

DATASET_DIR muss *train* und *test* Ordner enthalten.  
wird automatisch für beide ausgeführt und wandelt .txt in .xml um.


## 3 Pascal VOC zu CSV 

Inhalte der .xml files in ein *train.csv* und ein *test.csv*
achreiven:  
| filename | width | height | class | xmin | ymin | xmax | ymax |

dafür folgendes sycript ausführen:
```bash
python3 pascal_voc_xml_to_csv.py -i path/to/DATASET_DIR/
```

Wird automatisch für train und test Ordner in DATASET_DIR Ordner ausgeführt.


## 4 CSV zu TF Records

Beide CSV Files *train.csv* und *test.csv* können jetzt in TF Record Files convertiert werden.  

dafür jeweils für train und test seperat folgendes script ausführen

falls noch nicht vorhanden *classes.txt* erstellen, mit auflistung 
aller klassen namen.


```bash
python3 csv_to_tf_record.py \
  --csv_input path/to/DATASET_DIR/train.csv \
  --classes path/to/DATASET_DIR/classes.txt
```
und
```bash
python3 csv_to_tf_record.py \
  --csv_input path/to/DATASET_DIR/test.csv \
  --classes path/to/DATASET_DIR/classes.txt
```

## 5 LabelMap erstellen

Label Format für TFObj Det Api mit folgendem Script 
aus *classes.txt* file erzeugen.

```bash
python3 create_label_map.py classes.txt
```

## 6 data Ordner für training vorbereiten

```bash
└── DATASET_DIR
    └── data
        ├── train.record
        ├── test.record
        └── label_map.pbtxt
```



