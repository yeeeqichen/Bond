import numpy
import json
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import os
# 加载use模型
os.environ["TFHUB_CACHE_DIR"] = "//data/IE/windeye_data/tfhub_cache"
module_url = "https://hub.tensorflow.google.cn/google/universal-sentence-encoder-multilingual/3"
embed = hub.load(module_url)


class Config:
    def __init__(self):
        self.folder_path = '/data/IE/yqc/bond'
        self.top_k = 10
        self.embed_file_full = self.folder_path + '/name_embeddings.json'
        self.embed_file_short = self.folder_path + '/short_embeddings.json'
        self.labeled_text = self.folder_path + '/labeled_text.txt'
        self.name_file = self.folder_path + '/names.txt'
        self.names = []
        self.full_embeddings = []
        self.short_embeddings = []
        self.thresh_hold = 0.95


config = Config()
print('loading files...')
with open(config.name_file) as f:
    for name in f:
        config.names.append(name)
with open(config.embed_file_full) as f:
    for line in f:
        config.full_embeddings.append(numpy.array(json.loads(line.strip('\n'))))
with open(config.embed_file_short) as f:
    for line in f:
        config.short_embeddings.append(numpy.array(json.loads(line.strip('\n'))))
print('done')
