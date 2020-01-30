import tensorflow as tf
import keras
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from keras.utils import to_categorical


# Get the dataset
from keras.datasets import cifar10
(train_images, train_labels), (test_images, test_labels) = cifar10.load_data()

# pixelwerte der bilder von 0-255 auf 0-1 skalieren
train_images = train_images / 255
test_images = test_images / 255

# labels von integers von 0-9 in 10 binäre outputs 0,1 encodieren
train_labels = to_categorical(train_labels)
test_labels = to_categorical(test_labels)


def createModel():
    model = Sequential()
    # The first two layers with 32 filters of window size 3x3
    model.add(Conv2D(32, (3, 3), padding='same',
                     activation='relu', input_shape=train_images[0].shape))
    # model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(
        64, (3, 3), padding='same', activation='relu'))
    # model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    # model.add(Conv2D(
    #     64, (3, 3), padding='same', activation='relu'))
    # model.add(Conv2D(64, (3, 3), activation='relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(train_labels.shape[1], activation='softmax'))

    return model


model = createModel()
model.compile(optimizer='adam',
              loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(train_images, train_labels, batch_size=256, epochs=10, verbose=1,
                    validation_data=(test_images, test_labels))

model.save_weights('model_weights.h5')
# model.load_weights('model_weights.h5')

print(model.evaluate(test_images, test_labels))

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

