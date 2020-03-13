# Datenaugmentierung

## data_augmentation.py

Argumente:
* *train_dir*: Ordner der zu augmentierende Bilder enthält
(auch rekursiv)
* *n_max* Anzahl an Bilder die je Klasse erzeugt werden sollen
* *color* Anzahl der *Augmenter* aus der Liste *color_augmenters* 
für jedes bild angewendet werden sollen 
* *geometric* Anzahl der *Augmenter* aus der Liste *geometric_augmenters* für jedes bild angewendet werden sollen
* *all* (optional) wie viele Augmentierungen je bilde 
angewendet werden sollen (ohne spezifizierung)


Beispielhafte Ausführung:
```bash
python3 data_augmentation.py -t train/ -n 3000 -c 1 -g 1
```

Der *train* Ordner muss die Klassen separat in
Unterordnern enthalten.
Die Label Files können im gleichem Ordner wie die Bilder 
oder in einem weiterem Unterordner sein.  
Bsp:
```bash
└── train
    ├── Deer
    │   ├── Label
    │   │   ├── img1.txt
    │   │   └── img2.txt
    │   ├── img1.jpg
    │   └── img2.jpg
    └── Fox
        └── ...
```

oder:
```bash
└── train
    ├── Deer
    │   ├── img1.txt
    │   ├── img1.jpg
    │   ├── img2.txt
    │   └── img2.jpg
    └── Fox
        └── ...
```

Augmentierungen stammen aus [imgaug](https://imgaug.readthedocs.io/en/latest/index.html) und sind in [data_augmentation.py](data_augmentation.py) in den Listen *color_augmenters* 
und *geometric_augmenters* difiniert.



## visualize_augmentations.py

Zum Anzeigen der Augmentierten Bilder mit eingezeichneter Bounding Box

dafür:

```bash
python3 visualize_augmentations.py path/to/folder
```
dabei wird anhand gleicher namen von Bild und Label-File
die Box zugeordnet und eingezeichnet.


## test_augmenters.ipynb

Jupyter Notebook zum testen verschiedener Augmentern aus
[imgaug](https://imgaug.readthedocs.io/en/latest/source/api.html)
auf Bilder in images/ Ordner.

* [test_augmenters.ipynb](test_augmenters.ipynb)
