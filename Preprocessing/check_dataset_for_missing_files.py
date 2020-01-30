import os
import sys

path = sys.argv[1]

# usage python3 check_dataset_for_missing_file.py

# sucht nach einzelnen bild oder label files in einem ordner

liste = dict()
for file in os.listdir(path):
    file_name = str(file)[:-len(str(file).split('.')[-1])-1]
    if file_name in liste:
        del liste[file_name]
    else:
        liste[file_name] = file

for file in liste.values():
    print(path + file + ' has not img/label file')
    # os.remove(path + '/' + file)
