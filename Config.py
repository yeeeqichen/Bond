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
import os
import time
from sklearn.neighbors import KDTree
from sklearn.decomposition import PCA

# 加载use模型


class Config:
    """
    该类用于实例化config对象，为项目提供各类超参以及数据
    """
    def __init__(self):
        self.folder_path = '/data/IE/yqc/bond'
        self.top_k = 10
        self.embed_file_full = self.folder_path + '/name_embeddings.json'
        self.embed_file_short = self.folder_path + '/short_embeddings.json'
        # self.labeled_text = self.folder_path + '/labeled_text.txt'
        self.name_file = self.folder_path + '/names.txt'
        self.full_to_id_file = self.folder_path + '/full_to_id.json'
        self.map_table_path = self.folder_path + '/map_table.txt'
        self.bond_kind = ['人民币债券', '美元债券', '超短期融资券', '短期融资券', '债务融资工具', '中期票据', '大额存单', '集合票据',
                          '项目收益票据', '资产支持商业票据', '资产支持票据', '资产支持专项计划', '资产证券化', '同业存单', '定期存款', '专项金融债券', '金融债券', '定期债务', '资本补充债券',
                          '资产支持收益凭证', '融资券', '一般债券', '专项债券', '国债', '建设债券', '央行票据', '中央银行票据', '地方政府债券',
                          '政府债券', '置换债券', '专项公司债券', '可转换公司债券', '公司债券', '资本债券', '企业债券', '项目收益债券', '私募债券', '私募债', '集合债券',
                          '资产支持证券', 'PPN', 'ABN', 'MTN', 'SCP', 'CP', 'CD', 'PRN', '专项债', '转2', '债券', '转债', '债', '#']
        self.short_character = ['PPN', 'ABN', 'MTN', 'SCP', 'CP', 'CD', 'PRN']
        self.map_table = dict()
        self.names = []
        self.short_names = []
        self.full_names = []
        self.full_embeddings = []
        self.short_embeddings = []
        self.thresh_hold = 0.72
        self.bond_clusters = [[] for _ in range(len(self.bond_kind))]
        self.reduced_bond_clusters = []
        self.neighbor_in_cluster = []
        self.pca_in_cluster = []
        self.pca = PCA(n_components=50)
        self.total_neighbor = None
        # 这两个list存储到kb索引的映射关系
        self.cluster_to_id = [[] for _ in range(len(self.bond_kind))]
        self.full_to_id = []
        self.use_USE = True
        self.is_news = False
        self.use_PCA = False
        print('use_USE: ', self.use_USE)
        print('use_PCA: ', self.use_PCA)
        print('is_news: ', self.is_news)

    def clustering(self):
        """
        该函数用于将债券名库按照债券类型进行划分，并在每个子集内建立KD-Tree用于加速近邻寻找
        :return: None
        """
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
        for cluster in self.bond_clusters:
            if len(cluster) == 0:
                self.pca_in_cluster.append(None)
                self.neighbor_in_cluster.append(None)
                self.reduced_bond_clusters.append([])
                continue
            # self.lsh_in_cluster.append(LSHForest(random_state=123).fit(numpy.array(cluster)))
            array = numpy.array(cluster)
            if self.use_PCA:
                self.pca_in_cluster.append(PCA(n_components=50).fit(array))
                self.reduced_bond_clusters.append(self.pca_in_cluster[-1].transform(array))
                self.neighbor_in_cluster.append(KDTree(self.reduced_bond_clusters[-1]))
            else:
                self.neighbor_in_cluster.append(KDTree(array))
        array = numpy.array(self.full_embeddings)
        if self.use_PCA:
            self.pca.fit(array)
            self.total_neighbor = KDTree(self.pca.transform(array))
        else:
            self.total_neighbor = KDTree(array)
        print('done')
        print('cur_time: ', time.ctime(time.time()))


config = Config()
# 从文件中读取债券名库及其embedding
if config.use_USE:
    import tensorflow as tf
    import tensorflow_hub as hub
    import tensorflow_text
    os.environ["TFHUB_CACHE_DIR"] = "//data/IE/windeye_data/tfhub_cache"
    module_url = "https://hub.tensorflow.google.cn/google/universal-sentence-encoder-multilingual/3"
    embed = hub.load(module_url)
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
            config.full_embeddings.append(json.loads(line.strip('\n')))
    with open(config.embed_file_short) as f:
        for line in f:
            config.short_embeddings.append(json.loads(line.strip('\n')))
    with open(config.map_table_path) as f:
        for line in f:
            names = line.strip('\n').split(' ')
            if len(names) == 2:
                if names[1] not in config.map_table:
                    config.map_table[names[1]] = names[0]
    print('done')
    print('cur_time: ', time.ctime(time.time()))
    config.clustering()
else:
    with open(config.name_file) as f:
        for name in f:
            config.names.append(name)
            full, short = name.strip('\n').split(' ')
            config.short_names.append(short)
            config.full_names.append(full)
        for idx1, short in enumerate(config.short_names):
            for idx2, kind in enumerate(config.bond_kind):
                if kind in short or kind == '#':
                    config.bond_clusters[idx2].append(short)
                    config.cluster_to_id[idx2].append(idx1)
        for idx1, full in enumerate(config.full_names):
            for idx2, kind in enumerate(config.bond_kind):
                if kind in full or kind == '#':
                    config.bond_clusters[idx2].append(full)
                    config.cluster_to_id[idx2].append(idx1)
