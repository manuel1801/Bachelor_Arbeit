import split_folders
import os
import tensorflow as tf

input_dir = '/media/manuel/DATA/Studium/BachelorArbeit/datasets/raw-img'
output_dir = '/media/manuel/DATA/Studium/BachelorArbeit/datasets/splt-img'
model_dir = '../models/model_v1.h5'

INPUT_SIZE = 224
BATCH_SIZE = 64

split_folders.ratio(input_dir, output_dir, ratio=(0.8, 0.2))
ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator


training_data_generator = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
    )
    
tesing_data_generator = ImageDataGenerator(rescale=1./255)

#training_set = training_data_generator.flow_from_directory(
#    'splt-img/train/', target_size=(INPUT_SIZE, INPUT_SIZE),
#     batch_size=BATCH_SIZE, class_mode='categorical')

test_set = tesing_data_generator.flow_from_directory(
    output_dir + '/val/', target_size=(INPUT_SIZE, INPUT_SIZE),
     batch_size=BATCH_SIZE, class_mode='categorical')

model = tf.keras.models.load_model(model_dir)

print(model.metrics_names, model.evaluate_generator(test_set))