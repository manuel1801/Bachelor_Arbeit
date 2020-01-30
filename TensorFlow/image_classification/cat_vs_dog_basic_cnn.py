import tensorflow as tf
import keras
import numpy as np
import matplotlib.pyplot as plt
import os
import random
import utils
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense

# from https://github.com/PacktPublishing/Neural-Network-Projects-with-Python/tree/master/Chapter04
# datase: https://www.microsoft.com/en-us/download/confirmation.aspx?id=54765


# Hyperparameter:
# anzahl an trainingsbeispielen die für ein gradient descent verwendet werden
BATCH_SIZE = 16
# iterations per epoch (typicaly n/batchsize)
STEPS_PER_EPOCH = 20000//BATCH_SIZE
# in einer epoche sieht das netz einmal jede trainings data
EPOCHS = 10
# röße der Filter Matrix (3,3)
FILTER_SIZE = 3
# je mehr desto bessere perfomance jodoch langsameres training
NUM_FILTERS = 32
# größe auf die alle bilder kompremiert werden
INPUT_SIZE = 32
# größe der bereichs der zu einem unit zusammen gefasst wird
MAXPOOL_SIZE = 2
OPTIMIZER = 'adam'
LOSS = 'binary_crossentropy'

src_folder = 'Dataset/PetImages/'

# Split dataset into train and test like:
# PetImages
# ├── Test
# │   ├── Cats
# │   └── Dogs
# └── Train
#     ├── Cats
#     └── Dogs
if not os.path.isdir(src_folder + 'train'):
    utils.train_test_split(src_folder)

# get dataset as ImageDataGenerator Object
training_set, test_set = utils.get_dataset(
    src_folder=src_folder, input_size=INPUT_SIZE, batch_size=BATCH_SIZE)

# create a Keras Sequential Model
model = utils.create_the_model(input_size=INPUT_SIZE, num_filters=NUM_FILTERS,
                               filter_size=FILTER_SIZE, maxpool_size=MAXPOOL_SIZE)

# Train the Model
model.compile(optimizer=OPTIMIZER, loss=LOSS,
              metrics=['accuracy'])

model.fit_generator(
    training_set, steps_per_epoch=STEPS_PER_EPOCH, epochs=EPOCHS, verbose=1)

model.save('models/cat_vs_dog.h5')

# Evaluate the Model
score = model.evaluate_generator(test_set, steps=100)
for idx, metric in enumerate(model.metrics_names):
    print("{}: {}".format(metric, score[idx]))
