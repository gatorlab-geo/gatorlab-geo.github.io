import os

parts = ['head.html', 'part1.html', 'tail.html']
output_file = 'index.html'

with open(output_file, 'w', encoding='utf-8') as outfile:
    for part in parts:
        part_path = os.path.join(os.path.dirname(__file__), part)
        with open(part_path, 'r', encoding='utf-8') as infile:
            outfile.write(infile.read())
            outfile.write('\n')

print(f"Successfully built {output_file}")
