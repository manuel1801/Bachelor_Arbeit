# **Applikation** 

### **Version1: Inferenz Logik**

Bewegungs erkennung soll sich selbst regulieren:  
wenn bewegung da aber nichts erkannt wird, static background neu setzten

entweder: 
* Frames bei erkannter Bewegung abspeichern.
* Zweiter Prozess inferiert (mit faster rcnn) und speicert erkannte bilder ab

oder: 

* Frames bei erkannter Bewegung direkt inferieren (mit ssd und niedr threshhold)
* bounding boxes mit classifier auswerten

### **Version 2: Tcp-Connection**

* Aplikation (Server)
    * sendet nach bestimmten vorgaben (zB erkannte frames > 10) ein oder mehrere frames zu pc (client)

* Client
    *  kann aktuelles frame anfordern,
    *  tag/nacht modus wechseln (wenn funktionert),
    *  Modell/Inferenz Logik wechseln (wenn beide implementiert)

### **Version 3: Infrarot Modus**
entweder:
* mit aktueller Kamera mit GPIOs wie [hier](https://www.amazon.de/gp/product/B07KG8Y8SV/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&th=1) oder mit Schaltung wie [hier](https://forum-raspberrypi.de/forum/thread/42215-ir-led-nur-bei-bedarf-anschalten/)
* oder neue Kamera kaufen zb [RPiCam V2](https://www.amazon.de/LABISTS-Offizielle-Raspberry-V2-1-Kamera-Modul/dp/B07VSLZJCX/ref=sr_1_7?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=5E01AQS2BIJ4&keywords=raspberry+pi+4+cam+v2+noir&qid=1578662051&s=computers&sprefix=rtasp%2Ccomputers%2C151&sr=1-7)



### **Version 4: mit Internet**

über zB:
*  LTE Modul
* GSM
* WiFi Stick
