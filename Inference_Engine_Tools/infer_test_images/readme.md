# Inferenz für Test Images

Zum inferieren von Testbildern und Vergleichen der Ergebnisse  

## Einstellungen in den Scripten:  

**dataset_dir** Pfad zu Ordnern, die zu inferierende Bilder enthalten  

entweder in unterordnern:

```bash
└── OI_Animals/validation
    ├── Deer/
    │   ├── img1.jpg
    │   ├── img2.jpg
    │   └── ...
    └── Fox/
        └── ...
```

oder direkt:
```
└── handy_bilder/
    ├── img1.jpg
    └── img2.jpg
```

**models_dir** Pfad zu Ordnern die OpenVino Modelle enthalten wie:

Bsp:
```
└── ssd_inception/
    ├── frozen_inference_graph.xml
    ├── frozen_inference_graph.bin
    └── exported_model (optional)
```

**eval_dir** Ausgabe Ordner für inferierte Bilder

**infer_images_list** Liste mit zu inferierenden datensatz Ordnern

## infer_images_auto.py

Erzeugt automatisch zu jedem Testdatensatz einen Ordner
*infer_result_<dataset_name>* mit Inferenz Ergebnissen
zu den inferierten Modellen in Ordnern *files__<model_name>*
und Links zu den Bildern in einem Ordne zum direkten Vergleich 
verschiedener Modelle *links__<vgl_config>*.


Folgende Einsellungen müssen festgelegt werden:

**max_images** zum Festlegen maximaler zu inferierender Bilder,
(0 für alle Bilder)

**test_config** *dict* aus Model konfigurationen zum Vergleichen:
* Key: Ordner in den Links der zu vergleichenden Bilder kommen
* Value: Modelle, die Verglichen Werden sollen (und in *models_dir* enthalten sind)



## infer_images.py

Mit auswahl des Datensatz aus allen in *infer_images_list* definierten
und des Models mit allen im Ordner *models_dir* befindlichen 
über einen user-input.

Erzeugt in *eval_dir* ordner *infer_results_<dataset_name>*
mit unterordnern *<model_name>* in dem die inferierten Bilder 
des ausgewählten Modells gespeichert werden und einem Ordner *all* 
in dem Links zu den inferierten Bildern aller Modelle erzeugt 
werden, zum besseren vergleich.



## detect_images.py

Wird von infer_images_auto.py und infer_images.py für die 
Inferenz zur Object detection verwendet.

Prüft zunächst ob ein exportierten Modell mit 
name *exported_model* vorhanden ist.
Wenn nicht erzeugt aus IR-Model-Files die *'frozen_inference_graph.xml'*
und *'frozen_inference_graph.bin'* heißen ein exec_model und 
exportiert dieses für die nächste ausführung als *exported_model*.

