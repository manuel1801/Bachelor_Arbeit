# Datenaugmentierung

## data_augmentation.py

Argumente:
* *train_dir*: ordner der zu augmentierende bilder enthällt
(auch rekursiv)

* *n_max* anzahl an bilder die je klasse erzeugt werden sollen
* *color* wieviel augmenter aus liste *color_augmenters* 
je bild angewendet werden sollen 
* *geometric* wieviel augmenter aus liste *geometric_augmenters* 
je bild angewendet werden sollen

* *all* (optional) wie viele augmentierungen je bilde 
angewendet werden sollen (ohne spezifizierung)


Bsp Anwendung:
```bash
python3 data_augmentation.py -t train/ -n 3000 -c 1 -g 1
```

Der *train* Ordner muss die Klassen seperat in
Unterordnern enthallten.
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

Augmentierungen stammen aus [imgaug](https://imgaug.readthedocs.io/en/latest/index.html) und sind in [data_augmentation.py](data_augmentation.py) in den listen *color_augmenters* 
und *geometric_augmenters* difiniert.



## visualize_augmentations.py

Zum Anzeigen der Augmentierten Bilder mit eingezeichneter Bounding Box

dafür:

```bash
python3 visualize_augmentations.py path/to/folder
```
dabei wird anhand gleicher namen von bild und label file
die box zugeordnet und eingezeichnet.


## test_augmenters.ipynb

Jupyter Notebook zum testen verschiedener Augmentern aus
[imgaug](https://imgaug.readthedocs.io/en/latest/source/api.html)
auf bilder in [*images*](images/) ordner.

* [test_augmenters.ipynb](test_augmenters.ipynb)
