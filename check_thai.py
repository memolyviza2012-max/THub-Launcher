import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

lines = open('main.py', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if re.search(r'[\u0E00-\u0E7F]', l):
        if '_(' not in l:
            print(f'{i+1}: {l.strip()}')
