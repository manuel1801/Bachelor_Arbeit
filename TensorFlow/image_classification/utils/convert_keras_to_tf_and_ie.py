import tensorflow as tf
from tensorflow.python.framework import graph_io
from tensorflow.keras.models import load_model
import os
import sys

'''
Usage: python3 convert_keras_to_tf_and_ie.py path/to/keras/model.h5
erstellt im gleichen verzeichnis:
tensorflow model pb
inference engine model: xml, bin
(model optimizer has to be installed)
'''

if len(sys.argv) > 1:
    keras_model = sys.argv[1]
else:
    keras_model = '../../models/model.h5'

tf_model = keras_model.replace('.h5', '.pb')

tf_model_dir = tf_model.rsplit('/', 1)[:-1][0]
tf_model_name = tf_model.rsplit('/', 1)[-1]

# Clear any previous session.
tf.keras.backend.clear_session()

def freeze_graph(graph, session, output, tf_model_name, tf_model_dir, save_pb_as_text=False):
    with graph.as_default():
        graphdef_inf = tf.graph_util.remove_training_nodes(graph.as_graph_def())
        graphdef_frozen = tf.graph_util.convert_variables_to_constants(session, graphdef_inf, output)
        graph_io.write_graph(graphdef_frozen, tf_model_dir, tf_model_name, as_text=save_pb_as_text)
        return graphdef_frozen

# This line must be executed before loading Keras model.
tf.keras.backend.set_learning_phase(0) 

model = load_model(keras_model)

session = tf.keras.backend.get_session()

INPUT_NODE = [t.op.name for t in model.inputs]
OUTPUT_NODE = [t.op.name for t in model.outputs]
print(INPUT_NODE, OUTPUT_NODE)
frozen_graph = freeze_graph(session.graph, session, [out.op.name for out in model.outputs], tf_model_name, tf_model_dir)

# get input shape as string
input_shape = list(model.input_shape)
input_shape[0] = 1
input_shape = str(input_shape).replace(' ', '')
os.system('python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py --input_model ' + tf_model + ' --output_dir ' + tf_model_dir + ' --input_shape ' + input_shape + ' --data_type FP16')
