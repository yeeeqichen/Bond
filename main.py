# coding=UTF-8
from Config import config
from EntityLinker import link
import json


if __name__ == '__main__':
    texts = []
    tags = []
    with open(config.labeled_text) as f:
        for line in f:
            dic = json.loads(line)
            texts.append(dic['text'])
            tags.append(dic['tags'])

    for text, tags in zip(texts, tags):
        print('*' * 20)
        print('text: ', text)
        for result in link(text, tags):
            print(result)



