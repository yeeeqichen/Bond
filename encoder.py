from Config import embed
from sys import argv
import json

folder_path = argv[1]
mode = argv[2]

file_path = folder_path + '/names.txt'
names = []
if mode == 'full':
    with open(file_path) as f:
        for line in f:
            names.append(line.strip('\n').split(' ')[0])
    outfile = folder_path + '/name_embeddings.json'
elif mode == 'short':
    with open(file_path) as f:
        for line in f:
            names.append(line.strip('\n').split(' ')[1])
    outfile = folder_path + '/short_embeddings.json'
else:
    raise Exception('Please clarify mode : full or short')

with open(outfile, 'w') as f:
    for cnt, name in enumerate(names):
        name_embed = embed(name).numpy().squeeze().tolist()
        if cnt % 1000 == 0:
            print(cnt)
        f.write(json.dumps(name_embed) + '\n')
