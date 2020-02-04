# Obj Det in Keras

wir [hier](https://github.com/lars76/object-localization)

erklärung:

in [fit_generator](https://keras.io/models/model/#fit_generator) von keras model als erstes arg selbst implementierten DateGen verwenden, der als Target die Bounding Boxes hat. Dafür von der Klasse [keras.utils.Sequence](https://keras.io/utils/#sequence) erben und die benötigten funktionen ausimplementieren: __get_item() gibt batch of tupil of image/coords zurück.

(bisherige csv Files müssten verwendet werden können)



oder (vorher checken ob von openvino unterstützt):

[How to Train an Object Detection Model with Keras](https://machinelearningmastery.com/how-to-train-an-object-detection-model-with-keras/)

[Faster R-CNN (object detection) implemented by Keras](https://towardsdatascience.com/faster-r-cnn-object-detection-implemented-by-keras-for-custom-data-from-googles-open-images-125f62b9141a)