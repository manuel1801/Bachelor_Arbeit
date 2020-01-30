import numpy as np
import cv2
import tensorflow as tf
from matplotlib import pyplot as plt

data_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

train_dir = '/media/manuel/DATA1/dataset/OIDv4_ToolKit/OID/Dataset/train'
validation_dir = '/media/manuel/DATA1/dataset/OIDv4_ToolKit/OID/Dataset/validation'
test_dir = '/media/manuel/DATA1/dataset/OIDv4_ToolKit/OID/Dataset/test'
batch_size = 25

train_data = data_gen.flow_from_directory(
    train_dir, target_size=(224, 224), batch_size=batch_size)
validation_data = data_gen.flow_from_directory(
    validation_dir, target_size=(224, 224), batch_size=batch_size)
test_data = data_gen.flow_from_directory(
    test_dir, target_size=(224, 224), batch_size=batch_size)


print(train_data[0][0].shape)
print(train_data[0][1].shape)


for i, (img_batch, label_batch) in enumerate(train_data):
    print(i)
    print(img_batch.shape)
    print(label_batch.shape)
    print('\n')


exit()

n = 5
fig, ax = plt.subplots(n, n)
for i in range(n*n):
    ax[int(i/len(ax)), i % len(ax)].imshow(train_data[0][0][i])
    ax[int(i/len(ax)), i % len(ax)].set_title(np.argmax(train_data[0][1][i]))
    ax[int(i/len(ax)), i % len(ax)].axis('off')

plt.show()
