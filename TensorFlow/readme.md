

### 4.2 vortrainierten Model herunterladen
[Tensorflow Object Detection Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md)

### 4.3 Config File

Das für das Model richtige [Config File](https://github.com/tensorflow/models/tree/master/research/object_detection/samples/configs) herunteer laden und folgende Stellen anpasse:  

```config
num_classes # anzahl der Klassen 
```

```
fine_tune_checkpoint "path/to/model_folder/model.ckpt" # pfad zum heruntergeladenen Model
```

```
train_input_reader: {
  tf_record_input_reader {
    input_path: "data/train.record"
  }
  label_map_path: "data/label_map.pbtxt"
}
# sowie für eval_input_reader
```
```
eval_config: {
  metrics_set: "coco_detection_metrics"
  num_examples: N_TEST  # entspricht Zeilenzahl aus test.csv
}
```
und anschließend auch in **data** Ordner verschieben.



## 5 Training
### 5.1 Training starten

```python
python3 paht/to/models/research/object_detection/model_main.py \
--pipeline_config_path=data/MODEL_CONFIG_FILE.config \
--model_dir=OUTPUT_DIR \
--alsologtostderr \
--num_train_steps=N_STEPS_TO_TRAIN
```
Falls Memory Error Auftreten die Batch Size im Config File veringern und erneut versuchen.

### 5.2 Visualisierung

```bash
tensorboard --logdir OUTPUT_DIR
```

### 5.3 Trainierten Tensorflow Graph Exportieren

```python
python3 path/to/models/research/object_detection/export_inference_graph.py \
    --input_type image_tensor \
    --pipeline_config_path data/MODEL_CONFIG_FILE.config \
    --trained_checkpoint_prefix OUTPUT_DIR/model.ckpt-NR \ 
    --output_directory DATASET_DIR/frozen_graph/
```

erzeugt einen Ordner *frozen_graph* der *frozen_inference_graph.pb* enthält.  
Kann jetzt mit **OpenVino Model Optimizer** für **InferenceEngine** konvertiert werden



## 10. TensorFlow Graph für OpenVino konvertieren

Der Exportierte TensorFlow Graph kann nun mit dem Model Optimizer von OpenVino für die Inference Engine konvertiert werden.

Dafür folgenden Command ausführen:

```python
python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py \
--input_model path/to/frozen_inference_graph.pb \
--output_dir path/to/export/model \
--tensorflow_use_custom_operations_config model_support.json \
--tensorflow_object_detection_api_pipeline_config path/to/pipeline.config \
--input_shape [1,h,w,3] \
--data_type FP16 \
--input image_tensor \
--output=detection_classes,detection_scores,detection_boxes,num_detections \
--reverse_input_channels
```
Je nach model das entsprechende model_support.json file aus */opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/* verwenden.  
Für SSD Modelle die in Tensorflow v1.14 trainiert wurden **ssd_support_api_v1.14.json**
(wenn nur konvertiert werden soll, also ohne training: ssd_support.json nehmen) 

input_shape aus config file übernehmen.
data_type für NCS2 immer FP16

Die dadurch erzeugten xml und bin files können nun für die Inferenz mit Open Vino verwendet werden.


