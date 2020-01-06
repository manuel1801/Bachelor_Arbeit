"""
original von ...
änderung: geht für train und test

python3 xml_to_csv.py -i DATASET_DIR

DATASET_DIR has to contain a train and a test folder
"""

import os
import glob
import pandas as pd
import argparse
import xml.etree.ElementTree as ET


def xml_to_csv(path):

    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height',
                   'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main():
    # Initiate argument parser
    parser = argparse.ArgumentParser(
        description="Sample TensorFlow XML-to-CSV converter")
    parser.add_argument("-i",
                        "--inputDir",
                        help="Path to the folder where the train and test folders are",
                        type=str)

    args = parser.parse_args()

    if(args.inputDir is None):
        args.inputDir = os.getcwd()

    assert(os.path.isdir(args.inputDir))

    for split in ['train', 'test']:
        xml_df = xml_to_csv(args.inputDir + split)
        xml_df.to_csv(args.inputDir + split + '.csv', index=None)
        print('Successfully converted xml to csv.')


if __name__ == '__main__':
    main()
