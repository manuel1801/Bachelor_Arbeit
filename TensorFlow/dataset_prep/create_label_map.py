import sys

# read classes.txt file into list
classes_path = sys.argv[1]
classes = [cl.strip() for cl in open(classes_path).readlines()]
# print(classes)

# template for one item
template = 'item {\n    id: Nr\n    name: \'CLASS_NAME\'\n}\n'
label_file_str = ''

# iterate through classes and append to string
for i, c in enumerate(classes):
    label_file_str += template.replace('Nr', str(i+1)).replace('CLASS_NAME', c)

f = open('/'.join(classes_path.split('/')[:-1]) + '/label_map.pbtxt', 'w')
f.write(label_file_str)
