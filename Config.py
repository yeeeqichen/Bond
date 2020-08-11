#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: Config.py
@time: 2020/8/11 5:16 下午
@desc:
"""
import numpy
import json
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import os
import time
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
        self.full_to_id_file = self.folder_path + '/full_to_id.json'
        self.bond_kind = ['人民币债券', '美元债券', '超短期融资券', '短期融资券', '债务融资工具', '中期票据', '大额存单', '集合票据',
                          '项目收益票据', '资产支持商业票据', '资产支持票据', '同业存单', '定期存款', '专项金融债券', '金融债券', '定期债务', '资本补充债券',
                          '资产支持收益凭证', '融资券', '一般债券', '专项债券', '国债', '建设债券', '央行票据', '中央银行票据', '地方政府债券',
                          '政府债券', '置换债券', '专项公司债券', '公司债券', '资本债券', '企业债券', '项目收益债券', '私募债券', '私募债', '集合债券',
                          '资产支持证券', 'PPN', 'ABN', 'MTN', 'SCP', 'CP', 'CD', 'PRN', '专项债', '转2', '债券', '转债', '债', '#']
        self.names = []
        self.short_names = []
        self.full_names = []
        self.full_embeddings = []
        self.short_embeddings = []
        self.thresh_hold = 0.8
        self.bond_clusters = [[] for _ in range(len(self.bond_kind))]
        # 这两个list存储到kb索引的映射关系
        self.cluster_to_id = [[] for _ in range(len(self.bond_kind))]
        self.full_to_id = []

    def clustering(self):
        print('clustering...')
        print('cur_time: ', time.ctime(time.time()))
        for idx1, short in enumerate(self.short_names):
            for idx2, kind in enumerate(self.bond_kind):
                if kind in short or kind == '#':
                    self.bond_clusters[idx2].append(self.short_embeddings[idx1])
                    self.cluster_to_id[idx2].append(idx1)
                    break
        for idx1, full in enumerate(self.full_names):
            for idx2, kind in enumerate(self.bond_kind):
                if kind in full or kind == '#':
                    self.bond_clusters[idx2].append(self.full_embeddings[idx1])
                    self.cluster_to_id[idx2].append(self.full_to_id[idx1])
                    break
        print('done')
        print('cur_time: ', time.ctime(time.time()))


config = Config()
# 从文件中读取债券名库及其embedding
print('loading files...')
print('cur_time: ', time.ctime(time.time()))
with open(config.full_to_id_file) as f:
    temp = json.loads(f.readline())
    for i in temp:
        config.full_to_id.append(i)
with open(config.name_file) as f:
    for name in f:
        config.names.append(name)
        full, short = name.strip('\n').split(' ')
        config.short_names.append(short)
        if '政府' in full and '专项债券' in full and '-' in full:
            full1, full2 = full.split('-')[:2]
            config.full_names.append(full1)
            config.full_names.append(full2)
        else:
            config.full_names.append(full)
with open(config.embed_file_full) as f:
    for line in f:
        config.full_embeddings.append(numpy.array(json.loads(line.strip('\n'))))
with open(config.embed_file_short) as f:
    for line in f:
        config.short_embeddings.append(numpy.array(json.loads(line.strip('\n'))))
print('done')
print('cur_time: ', time.ctime(time.time()))
config.clustering()
