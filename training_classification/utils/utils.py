import os
import random
import shutil
import piexif
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense



def get_dataset(src_folder='Dataset/PetImages/', input_size=32, batch_size=16, train_only=False, test_only=False):

    # prepare the data
    src_folder = 'Dataset/PetImages/'

    # rescale pixel values from 0..255 to 0..1 und evtl augmentierung
    training_data_generator = ImageDataGenerator(rescale=1./255)
    tesing_data_generator = ImageDataGenerator(rescale=1./255)

    # create the training and testing set with the flow_from_directory() Method
    training_set = training_data_generator.flow_from_directory(
        src_folder + 'Train/', target_size=(input_size, input_size), batch_size=batch_size, class_mode='binary')

    test_set = tesing_data_generator.flow_from_directory(
        src_folder + 'Test/', target_size=(input_size, input_size), batch_size=batch_size, class_mode='binary')

    if train_only == True:
        return training_set
    elif test_only == True:
        return test_set
    return (training_set, test_set)


def visualize(img, n=3):

    # img ist ImageDataGenerator mit [batch][img:0, label:1][img]

    fig, ax = plt.subplots(n, n)
    title = ['cat', 'dog']

    for i in range(n*n):
        ax[int(i/len(ax)), i % len(ax)].imshow(img[0][0][i])
        ax[int(i/len(ax)), i % len(ax)].set_title(title[int(img[0][1][i])])
        ax[int(i/len(ax)), i % len(ax)].axis('off')

    plt.show()


def create_the_model(input_size=32, num_filters=32, filter_size=3, maxpool_size=2):
    model = Sequential()

    model.add(Conv2D(num_filters, (filter_size, filter_size),
                     input_shape=(input_size, input_size, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(maxpool_size, maxpool_size)))
    model.add(Conv2D(num_filters, (filter_size, filter_size),
                     input_shape=(input_size, input_size, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(maxpool_size, maxpool_size)))
    model.add(Flatten())
    model.add(Dense(units=128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(units=1, activation='sigmoid'))
    return model
