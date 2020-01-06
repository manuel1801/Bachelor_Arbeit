#!/bin/bash

# ohne / am ende
dataset_dir=$1

# 1. python3 remove_spaces.py

# 2. collect files from subfolders
./collect_files_from_subfolders.sh $dataset_dir

# 3. convert oi txt labels to pascal voc xml labels
python3 oi_to_pascal_voc_xml.py --dataset_path $dataset_dir/

# 4. convert the pascal voc xml labels to csv files
python3 pascal_voc_xml_to_csv.py -i $dataset_dir/

# optional classes file automatsich erzeugen

# 5. convert the csv and image files to tf record files 
python3 csv_to_tf_record.py --csv_input=$dataset_dir/train.csv --image_dir=$dataset_dir/train/ --classes=$dataset_dir/classes.txt
python3 csv_to_tf_record.py --csv_input=$dataset_dir/test.csv --image_dir=$dataset_dir/test/ --classes=$dataset_dir/classes.txt

python3 create_label_map.py $dataset_dir/classes.txt
