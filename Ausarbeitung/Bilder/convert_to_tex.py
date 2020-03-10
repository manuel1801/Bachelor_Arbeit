import os
import subprocess
import sys

#svg_dir = '/home/manuel/Bachelor_Arbeit/Vortrag/vortrag/Bilder'
svg_dir = '/home/manuel/Bachelor_Arbeit/Ausarbeitung/Bilder'
if len(sys.argv) > 1:
    svg_dir = sys.argv[1]

svg_files = [f[:-4] for f in os.listdir(svg_dir) if f[-3:] == 'svg']
for name in svg_files:
    name_dir = os.path.join(svg_dir, name)
    subprocess.call(['inkscape', '-D', '-z', '--file', name_dir + '.svg',
                     '--export-pdf', name_dir + '.pdf', '--export-latex'])
