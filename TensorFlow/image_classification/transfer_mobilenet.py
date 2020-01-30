import tensorflow as tf
import keras
import numpy as np
from matplotlib import pyplot as plt
from keras.layers import Dense, GlobalAveragePooling2D, Dropout
from keras.optimizers import Adam
from keras.applications.mobilenet_v2 import preprocess_input
from keras.applications import MobileNetV2
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator
from keras.metrics import categorical_crossentropy
from keras.optimizers import Adam
from keras.layers.core import Dense, Activation
from keras import backend as K
from PIL import ImageFile
# ImageFile.LOAD_TRUNCATED_IMAGES = True

# import split_folders
# split_folders.ratio('FlickrAnimals/', output="FlickrAnimals/", seed=1337, ratio=(.8, .1, .1)) # default values


dataset_dir = '/home/manuel/Bachelor_Arbeit/TensorFlow/workspace/Flickr_Animals_Classification/'

# imports the mobilenet model and discards the last 1000 neuron layer.
base_model = MobileNetV2(weights='imagenet', include_top=False)

x = base_model.output
x = GlobalAveragePooling2D()(x)
# we add dense layers so that the model can learn more complex functions and classify for better results.
x = Dense(1024, activation='relu')(x)
# x=Dropout(0.3)(x)
x = Dense(1024, activation='relu')(x)  # dense layer 2
# x=Dropout(0.3)(x)
x = Dense(512, activation='relu')(x)  # dense layer 3
# x=Dropout(0.3)(x)
# final layer with softmax activation
preds = Dense(16, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=preds)

for layer in model.layers[:-4]:
    layer.trainable = False

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input)  # included in our dependencies


train_generator = train_datagen.flow_from_directory(dataset_dir + 'train',
                                                    target_size=(224, 224),
                                                    color_mode='rgb',
                                                    batch_size=32,
                                                    class_mode='categorical',
                                                    shuffle=True)

validation_generator = train_datagen.flow_from_directory(dataset_dir + 'validation',
                                                         target_size=(
                                                             224, 224),
                                                         color_mode='rgb',
                                                         batch_size=32,
                                                         class_mode='categorical')

test_generator = train_datagen.flow_from_directory(dataset_dir + 'test',
                                                   target_size=(224, 224),
                                                   color_mode='rgb',
                                                   batch_size=32,
                                                   class_mode='categorical',
                                                   shuffle=False)


model.compile(optimizer='Adam', loss='categorical_crossentropy',
              metrics=['accuracy'])


step_size_train = train_generator.n//train_generator.batch_size
validation_steps = test_generator.n // test_generator.batch_size

history = model.fit_generator(generator=train_generator,
                              steps_per_epoch=step_size_train,
                              epochs=10,
                              validation_data=validation_generator,
                              validation_steps=validation_steps,
                              verbose=1)

model.save('/home/manuel/Bachelor_Arbeit/TensorFlow/workspace/Flickr_Animals_Classification/flickr_animals_mobile_net.h5')
model.save_weights(
    '/home/manuel/Bachelor_Arbeit/TensorFlow/workspace/Flickr_Animals_Classification/flickr_animals_mobile_net_weights.h5')

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

model.evaluate(test_generator)
