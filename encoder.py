from sys import argv
import json
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import os

# 加载use模型
os.environ["TFHUB_CACHE_DIR"] = "//data/IE/windeye_data/tfhub_cache"
module_url = "https://hub.tensorflow.google.cn/google/universal-sentence-encoder-multilingual/3"
embed = hub.load(module_url)

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
