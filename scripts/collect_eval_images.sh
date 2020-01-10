#!/bin/bash

dataset_dir=$1

mkdir $dataset_dir/all
find $dataset_dir -name "*.jpg" -exec cp "{}" $dataset_dir/all/ \;