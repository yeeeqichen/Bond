#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: encoder.py
@time: 2020/8/11 5:16 下午
@desc:
"""
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
    full_to_id = []
    with open(outfile, 'w') as f:
        for cnt, name in enumerate(names):
            # 对于用'-'连接两个名字的债券，将两部分分别进行encode，并记录其到知识库中的索引
            if '政府' in name and '专项债券' in name and '-' in name:
                name1, name2 = name.split('-')[:2]
                name_embed = embed(name1).numpy().squeeze().tolist()
                f.write(json.dumps(name_embed) + '\n')
                full_to_id.append(cnt)
                name_embed = embed(name2).numpy().squeeze().tolist()
                f.write(json.dumps(name_embed) + '\n')
                full_to_id.append(cnt)
            else:
                name_embed = embed(name).numpy().squeeze().tolist()
                f.write(json.dumps(name_embed) + '\n')
                full_to_id.append(cnt)
            if cnt % 1000 == 0:
                print(cnt)
    with open(folder_path + '/full_to_id.json', 'w') as f:
        f.write(json.dumps(full_to_id))

elif mode == 'short':
    with open(file_path) as f:
        for line in f:
            names.append(line.strip('\n').split(' ')[1])
    outfile = folder_path + '/short_embeddings.json'
    with open(outfile, 'w') as f:
        for cnt, name in enumerate(names):
            name_embed = embed(name).numpy().squeeze().tolist()
            if cnt % 1000 == 0:
                print(cnt)
            f.write(json.dumps(name_embed) + '\n')
else:
    raise Exception('Please clarify mode : full or short')


