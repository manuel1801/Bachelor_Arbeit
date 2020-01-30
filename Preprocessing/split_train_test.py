import os
import sys

'''
teilt inhalt eines ordners auf zwei train und test auf
im Verhältnis train=ratio test=(1-ratio) 
'''

# usage: python3 split_train_test dataset_folder ratio

dataset = sys.argv[1]  # mit / am ende
ratio = float(sys.argv[2])  # zb. 0.8


try:
    os.mkdir('tmp_train')
    os.mkdir('tmp_test')
    os.mkdir('tmp_images')
except OSError:
    None

n_samples = len(os.listdir(dataset)) / 2


for i, file in enumerate(os.listdir(dataset)):
    if file.split('.')[-1] == 'xml':
        if (i/2 + 1) / n_samples <= ratio:
            os.rename(dataset + file, 'tmp_train/' + file)
        else:
            os.rename(dataset + file, 'tmp_test/' + file)
    else:
        os.rename(dataset + file, 'tmp_images/' + file)

os.rename('tmp_train', dataset + 'train')
os.rename('tmp_test', dataset + 'test')
os.rename('tmp_images', dataset + 'images')
