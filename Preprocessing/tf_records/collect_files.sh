#!/bin/bash

dataset_dir=$1

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

