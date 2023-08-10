#!/usr/bin/python

import sys, os, re

def h_to_link(h, n):
    hashes = '#' * n
    m = re.search('^' + hashes + ' (.*)', h)
    if m:
        text = m[1]
        indent = ' ' * 4 * (n-1)
        # lower case, remove non-alphabetic and replace space with -
        link = "".join(c for c in text if c.isalpha() or c == ' ').lower().replace(' ','-')
        # If we used a : in the heading, remove it from TOC because it looks bad
        return f"{indent}- [{text.rstrip(':')}](#{link})  "
    return None

# Read given file, or from STDIN
if len(sys.argv) == 1:
    lines = sys.stdin.readlines()
else:
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()

# Remove code blocks so that # inside code is not misinterpreted as a heading:
nocode_lines = []
in_block = False
for line in lines:
    if line.startswith('```'):
        in_block = not in_block
    if not in_block:
        nocode_lines.append(line)

headings = [h for h in nocode_lines if re.search('^#', h)]

import subprocess
print(f"Documentation generated from: {subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')}")

for tocline in [h_to_link(h, n) for h in headings for n in range(1,5) if h_to_link(h, n)]:
	print(tocline)
