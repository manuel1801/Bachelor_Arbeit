import os
from keras.applications.vgg16 import VGG16
from keras.layers import Flatten, Dense
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator

INPUT_SIZE = 128
# Load the VGG16 Model without the Fully Connected Layers with include_top=False
vgg16 = VGG16(include_top=False, weights='imagenet',
              input_shape=(INPUT_SIZE, INPUT_SIZE, 3))

# freeze the Convolutianal Layers
for layer in vgg16.layers:
    layer.trainable = False

# add fully connected layer to the vgg
# (since its not a Sequential Model it has to be done manually insted of add())
input_ = vgg16.input
output_ = vgg16(input_)
last_layer = Flatten(name='flatten')(output_)
last_layer = Dense(1, activation='sigmoid')(last_layer)
model = Model(input=input_, output=last_layer)

# Definfe Hyperparameters
BATCH_SIZE = 16
STEPS_PER_EPOCH = 200
EPOCHS = 5

# compile the model
model.compile(optimizer='adam', loss='binary_crossentropy',
              metrics=['accuracy'])


# prepare the data
src_folder = 'Dataset/PetImages/'
if not os.path.isdir(src_folder + 'train'):
    train_test_split(src_folder)

# rescale pixel values from 0..255 to 0..1
training_data_generator = ImageDataGenerator(rescale=1./255)
tesing_data_generator = ImageDataGenerator(rescale=1./255)

# create the training and testing set with the flow_from_directory() Method
training_set = training_data_generator.flow_from_directory(
    src_folder + 'Train/', target_size=(INPUT_SIZE, INPUT_SIZE), batch_size=BATCH_SIZE, class_mode='binary')

test_set = tesing_data_generator.flow_from_directory(
    src_folder + 'Test/', target_size=(INPUT_SIZE, INPUT_SIZE), batch_size=BATCH_SIZE, class_mode='binary')

# train the model with the training set
model.fit_generator(
    training_set, steps_per_epoch=STEPS_PER_EPOCH, epochs=EPOCHS, verbose=1)

model.save('models/vgg16_model.h5')

# evaluate the model with the test set
score = model.evaluate_generator(test_set, len(test_set))
for idx, metric in enumerate(model.metrics_names):
    print('{}: {}:'.format(metric, score[idx]))
