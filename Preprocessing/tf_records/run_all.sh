#!/bin/bash

# Argument: path/to/dataset (ohne  '/' am ende)
# dataset enthällt 'train', 'test', und 'classes.txt'
# ausführen aus diesem ordner
 
dataset_dir=$1

# 1. python3 remove_spaces.py
# remove_spaces.py

# 2. collect files from subfolders
mkdir $dataset_dir/train/labels
find $dataset_dir/train/ -name "*.txt" -exec mv "{}" $dataset_dir/train/labels/ \;
find $dataset_dir/train/ -name "*.jpg" -exec mv "{}" $dataset_dir/train/ \;

mkdir $dataset_dir/test/labels
find $dataset_dir/test/ -name "*.txt" -exec mv "{}" $dataset_dir/test/labels/ \;
find $dataset_dir/test/ -name "*.jpg" -exec mv "{}" $dataset_dir/test/ \;

mkdir $dataset_dir/validation/labels
find $dataset_dir/validation/ -name "*.txt" -exec mv "{}" $dataset_dir/validation/labels/ \;
find $dataset_dir/validation/ -name "*.jpg" -exec mv "{}" $dataset_dir/validation/ \;

find $dataset_dir/ -depth -type d -empty -exec rmdir {} \;


# 3. convert oi txt labels to pascal voc xml labels
python3 oi_to_pascal_voc_xml.py --dataset_path $dataset_dir/

# 4. convert the pascal voc xml labels to csv files
python3 pascal_voc_xml_to_csv.py -i $dataset_dir/


# 5. convert the csv and image files to tf record files 
python3 csv_to_tf_record.py --csv_input=$dataset_dir/train.csv --image_dir=$dataset_dir/train/ --classes=$dataset_dir/classes.txt
python3 csv_to_tf_record.py --csv_input=$dataset_dir/test.csv --image_dir=$dataset_dir/test/ --classes=$dataset_dir/classes.txt

# 6. label_map.pbtxt aus classes.txt erzeugen
python3 create_label_map.py $dataset_dir/classes.txt
