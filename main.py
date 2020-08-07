# coding=UTF-8
from Config import config
from EntityLinker import link
import json
from sys import argv

mode = argv[1]
num = argv[2]
if __name__ == '__main__':
    texts = []
    tags = []
    if mode == 'test':
        path = config.folder_path + '/samples{}.txt'.format(num)
    else:
        path = config.labeled_text
    with open(path) as f:
        for line in f:
            dic = json.loads(line)
            texts.append(dic['text'])
            tags.append(dic['tags'])

    for text, tags in zip(texts, tags):
        print('*' * 20)
        print('text: ', text)
        for result in link(text, tags):
            print(result)



