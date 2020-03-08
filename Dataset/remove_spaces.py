import os
import subprocess
import sys

# python3 remove_spaces.py path/to/folder

# sucht in allen unterordnern nach text files,
# prüft ob class name aus 2 wörtern besteht,
# falls ja ersetzt ' ' mit '_'

dataset_dir = sys.argv[1]

pr = subprocess.Popen(['find', dataset_dir, '-name', '*.txt'],
                      stdout=subprocess.PIPE)

paths = [p.decode('utf-8').strip() for p in pr.stdout.readlines()]

for path in paths:
    lines = []
    with open(path, 'r') as fin:
        for line in fin:
            if not line.split(' ')[1].replace('.', '', 1).isdigit():
                line = line.replace(' ', '_', 1)
            lines.append(line)

    with open(path, 'w') as fout:
        for line in lines:
            fout.write(line)
