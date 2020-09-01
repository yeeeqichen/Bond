#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: test.py
@time: 2020/8/14 10:08 上午
@desc:
"""
# from EntityLinker import link
import json
import os
from sys import argv
import random
files = []
string = argv[1]
for filename in os.listdir('/users/maac/desktop/res_news'):
    with open('/users/maac/desktop/res_news/' + filename) as f:
        file = json.loads(f.read())
        files.append((file, filename))
        # print('*' * 30)
# random.shuffle(files)
cnt = 0
# with open('/users/maac/desktop/new_badcase/case9', 'w') as f:
for s in files:
    article = ''
    for dic in s[0]:
        if dic['type'] == 'text':
            article += dic['text']
    if string in article:
        # with open('/users/maac/desktop/news_badcase5.txt', 'a+') as f:
        #     f.write(s[1] + '\n')
        print(article)
        # f.write(json.dumps(s, ensure_ascii=False))

