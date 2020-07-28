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


# todo:xx政府专项债券-xx政府专项债券，考虑将这种情况拆分成两个债券
class Config:
    def __init__(self):
        self.folder_path = '/data/IE/yqc/bond'
        self.top_k = 10
        self.embed_file_full = self.folder_path + '/name_embeddings.json'
        self.embed_file_short = self.folder_path + '/short_embeddings.json'
        self.labeled_text = self.folder_path + '/labeled_text.txt'
        self.name_file = self.folder_path + '/names.txt'
        self.bond_kind = ['人民币债券', '美元债券', '短期融资券', '超短期融资券', '债务融资工具', '中期票据', '大额存单', '集合票据',
                          '项目收益票据', '资产支持商业票据', '资产支持票据', '同业存单', '定期存款', '专项金融债券', '金融债券', '定期债务', '资本补充债券',
                          '资产支持收益凭证', '融资券', '一般债券', '专项债券', '国债', '建设债券', '央行票据', '中央银行票据', '地方政府债券',
                          '政府债券', '置换债券', '专项公司债券', '公司债券', '资本债券', '企业债券', '项目收益债券', '私募债券', '私募债', '集合债券',
                          '资产支持证券', 'PPN', 'ABN', 'MTN', 'SCP', 'CP', 'CD', 'PRN', '专项债', '债券', '债', '#']
        self.names = []
        self.full_embeddings = []
        self.short_embeddings = []
        self.thresh_hold = 0.8
        self.bond_clusters = [[] for _ in range(len(self.bond_kind))]
        self.cluster_to_id = [[] for _ in range(len(self.bond_kind))]

    def clustering(self):
        print('clustering...')
        for idx1, name in enumerate(self.names):
            full, short = name.strip('\n').split(' ')
            for idx2, kind in enumerate(self.bond_kind):
                if kind in full or kind == '#':
                    self.bond_clusters[idx2].append(self.full_embeddings[idx1])
                    self.cluster_to_id[idx2].append(idx1)
                    break
            for idx2, kind in enumerate(self.bond_kind):
                if kind in short or kind == '#':
                    self.bond_clusters[idx2].append(self.short_embeddings[idx1])
                    self.cluster_to_id[idx2].append(idx1)
                    break
        print('done')


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
config.clustering()
# print(len(config.full_embeddings))
# print(len(config.short_embeddings))