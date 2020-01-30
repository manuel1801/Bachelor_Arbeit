# !/usr/bin/env python
"""
 Copyright (c) 2018 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the 'License');
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an 'AS IS' BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""


import os
import sys

import argparse

from pathlib import Path

import tensorflow as tf
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

from keras import backend as K
from keras.models import load_model


def setKerasOptions():
    K._LEARNING_PHASE = tf.constant(0)
    K.set_learning_phase(False)
    K.set_learning_phase(0)
    K.set_image_data_format('channels_last')


def getInputParameters():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_model', '-m', required=True, type=str, help='Path to Keras model.')
    parser.add_argument('--num_outputs', '-no', required=False, type=int, help='Number of outputs. 1 by default.', default=1)

    return parser


def export_keras_to_tf(input_model, output_model, num_output):
    print('Loading Keras model: ', input_model)

    keras_model = load_model(input_model)

    print(keras_model.summary())

    predictions = [None] * num_output
    predrediction_node_names = [None] * num_output

    for i in range(num_output):
        predrediction_node_names[i] = 'output_node' + str(i)
        predictions[i] = tf.identity(keras_model.outputs[i], name=predrediction_node_names[i])

    sess = K.get_session()

    constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), predrediction_node_names)
    infer_graph = graph_util.remove_training_nodes(constant_graph) 

    graph_io.write_graph(infer_graph, '.', output_model, as_text=False)


def main():
    argv = getInputParameters().parse_args()

    input_model = argv.input_model
    num_output = argv.num_outputs
    output_model = str(Path(input_model).name) + '.pb'
    
    predrediction_node_names = export_keras_to_tf(input_model, output_model, num_output)

    print('Ouput nodes are:', predrediction_node_names)
    print('Saved as TF frozen model to: ', output_model)


if __name__ == '__main__':
  main()