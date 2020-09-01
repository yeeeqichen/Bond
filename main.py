#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: main.py
@time: 2020/8/13 4:37 下午
@desc:
"""
from EntityLinker import link
import json
from Config import config
import os
import random
import time
from sys import argv

mode = argv[1]
num = argv[2]
if mode == 'test':
    if config.is_news:
        sample_path = 'news_test_samples{}.txt'
        oracle_path = 'news_oracle{}.txt'
    else:
        sample_path = 'test_samples{}.txt'
        oracle_path = 'oracle{}.txt'
    begin_time = time.time()
    with open(sample_path.format(num)) as f:
        samples = json.loads(f.read())
    results = []
    with open(oracle_path.format(num)) as f:
        title = f.readline()
        while title != 'EOF\n':
            # print(title)
            result = json.loads(f.readline())
            results.append(result)
            _ = f.readline()
            title = f.readline()
    assert (len(samples) == len(results))
    total = 0
    hit = 0
    special_case = 0
    for sample, oracle in zip(samples, results):
        title_result, article_result, title, article = link(sample)
        if len(oracle) != len(title_result):
            if len(oracle) == 0 and len(title_result) == 1:
                if title_result[0]['entity'] == ['entity not find in knowledge base!']:
                    hit += 1
                    continue
            print(title)
            print('oracle:', oracle)
            print('predict:', title_result)
            continue
        correct = True
        flag = 0
        for pre, gold in zip(title_result, oracle):
            for entity1, entity2 in zip(pre['entity'], gold['entity']):
                if config.use_USE:
                    if len(entity1) == 0 or len(entity2) == 0:
                        continue
                    if entity2 == 'entity not find in knowledge base!':
                        flag = 1
                    full1, short1 = entity1.split(' ')[:2]
                    full2, short2 = entity2.split(' ')[:2]
                    if not(full1 == full2 or short1 == short2):
                        correct = False
                else:
                    if entity1 in entity2:
                        hit += 1
                    else:
                        correct = False
        if not correct:
            print(title)
            print('oracle:', oracle)
            print('predict:', title_result)
        else:
            hit += 1
        if flag:
            special_case += 1
    end_time = time.time()
    print('total time cost: ', end_time - begin_time)
    print(len(samples))
    print(hit)
    print(hit / len(samples))
    print('cases that bond not in knowledge: ', special_case)
elif mode == 'sample':
    if config.is_news:
        path = '/data/IE/yqc/bond/res_news'
        out_file = 'news_test_samples{}.txt'
    else:
        path = '/data/IE/yqc/bond/bond_arg_ner_res'
        out_file = 'test_samples{}.txt'
    files = []
    for filename in os.listdir(path):
        with open(path + '/' + filename) as f:
            file = json.loads(f.read())
            files.append(file)
            # print('*' * 30)
    random.shuffle(files)
    files = files[:200]
    samples = []
    for file in files:
        title_result, article_result, title, article = link(file)
        if len(title) > 200:
            continue
        samples.append(file)
    with open(out_file.format(num), 'w') as f:
        f.write(json.dumps(samples, ensure_ascii=False))
elif mode == 'train':
    if config.is_news:
        path = 'news_test_samples{}.txt'
    else:
        path = 'test_samples{}.txt'
    cnt = 0
    with open(path.format(num)) as f:
        samples = json.loads(f.read())
    print(len(samples))
    for file in samples:
        title_result, article_result, title, article = link(file)
        print(title)
        print(json.dumps(title_result, ensure_ascii=False))
        print('')
        # print('*' * 80)
        # print(title)
        # print('title:')
        # for r in title_result:
        #     print(r)
        # print('article:')
        # for r in article_result:
        #     print(r)
elif mode == 'dev':
    files = []
    for f in os.listdir('/data/IE/yqc/bond/bond_arg_ner_res'):
        files.append(f)
        random.shuffle(files)
    for f in files:
        with open('/data/IE/yqc/bond/bond_arg_ner_res/' + f) as q:
            file = json.loads(q.read())
        title_result, article_result, title, article = link(file)
        print('*' * 80)
        print(title)
        print('title:')
        for r in title_result:
            print(r)
        print('article:')
        for r in article_result:
            print(r)
