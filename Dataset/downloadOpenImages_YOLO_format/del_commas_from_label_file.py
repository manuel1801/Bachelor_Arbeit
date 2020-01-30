import os
import sys

# python renameClasses.py dataset_dir

dataset_dir = sys.argv[1]

for mode in ['train/', 'test/', 'validation/']:

    path = dataset_dir + mode + 'labels/'

    for file in os.listdir(path):
        if(file.split('.')[-1] == 'txt'):
            lines = []
            with open(path + '/' + file) as fin:
                for line in fin:
                    line = line.replace(',', ' ')
                    lines.append(line)
            with open(path + '/' + file, 'w') as fout:
                for line in lines:
                    fout.write(line)
