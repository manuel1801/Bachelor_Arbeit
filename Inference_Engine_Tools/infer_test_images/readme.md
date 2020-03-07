# Infer Test Images

Zum inferieren von Testbildern und Vergleichen der Ergebnisse  

## infer_images_auto

Erzeugt automatisch zu jedem Testdatensatz einen Ordner
*infer_result_<dataset_name>* mit Inferenz Ergebnissen
zu den inferierten Modellen in Ordnern *files__<model_name>*
und Links zu den Bildern in einem Ordne zum direkten Vergleich 
verschiedener Modelle *links__<vgl_config>*.


### Verwendung:

Folgende Einsellungen müssen festgelegt werden:

**dataset_dir** Pfad zu Ordnern, die zu inferierende Bilder enthalten  

entweder in unterordnern:
* OI_Animals/validation
    * Deer/
        * img1.jpg
        * img2.jpg
        * ...
    * Fox/
        * ...

oder direkt:
* handy_bilder/
    * img1.jpg
    * img2.jpg


**models_dir** Pfad zu Ordnern die OpenVino Models enthalten wie:

Bsp:
* ssd_inception/
    * frozen_inference_graph.xml
    * frozen_inference_graph.bin
    * exported_model (optional)

**eval_dir** Ausgabe Ordner für inferierte Bilder

**infer_images_list** Liste mit zu inferierenden datensatz Ordnern

**max_images** zum Festlegen maximaler zu inferierender Bilder,
(0 für alle Bilder)

**test_config** dict aus Model konfigurationen zum Vergleichen:
* Key: Ordner in den Links der zu vergleichenden Bilder kommen
* Value: Modelle, die Verglichen Werden sollen


## infer_images

inferieren von einem bestimmten Datensatz auf nur ein Model:

