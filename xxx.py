#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: xxx.py
@time: 2020/8/25 3:57 下午
@desc:
"""
import json
from sys import argv
num = argv[1]
labeled_data = []
files = []
with open('/Users/maac/Desktop/news_badcase{}.txt'.format(num)) as f:
    for line in f:
        files.append('/users/maac/desktop/res_news/' + line.strip('\n'))
with open('/users/maac/desktop/news_text{}.txt'.format(num), 'w') as outfile:
    for file in files:
        text = ''
        tags = []
        with open(file) as f:
            news = json.loads(f.read())
            cnt = 0
            for sent in news:
                if sent['type'] != 'text' or sent['paragraph'] == 'title':
                    continue
                # print(int(sent['paragraph']))
                text += sent['text']
                tags += sent['bond_arg']
                cnt += 1
                if cnt == 2:
                    outfile.write(json.dumps(dict({'text': text, 'tags': tags}), ensure_ascii=False) + '\n')
                    cnt = 0
                    text = ''
                    tags = []
            if len(text) != 0:
                outfile.write(json.dumps(dict({'text': text, 'tags': tags}), ensure_ascii=False) + '\n')
        labeled_data.append(dict({'text': text, 'tags': tags}))
# with open('/users/maac/brat/data/Bond/News.txt', 'w') as f:
#     for news in labeled_data:
#         f.write(news['text'] + '\n')

