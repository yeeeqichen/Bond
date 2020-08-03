# coding=UTF-8
from Config import config
from EntityLinker import entity_linker
import json
from Merge import merge_elements


def get_mentions(_blocks):
    """
    :param _blocks:每个block表示一只债券
    :return: 每只债券的mention，及其对应的债券类型，如果没有则返回 #
    """
    _mentions = []
    _bond_kinds = []
    for block in _blocks:
        mention = ''
        flag = 0
        for ele, kind in zip(block['elements'], block['tags']):
            mention += ele
            if kind == '债券类型':
                _bond_kinds.append(ele)
                flag = 1
        _mentions.append(mention)
        if flag == 0:
            _bond_kinds.append('#')
    return _mentions, _bond_kinds


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
        blocks = merge_elements(text, tags)
        mention_set, kind_set = get_mentions(blocks)
        if len(mention_set) == 0:
            print('no mention')
        else:
            candidates, predicts = entity_linker(text, mention_set, kind_set)
            for mention, candidate, predict in zip(mention_set, candidates, predicts):
                print('mention: ', mention)
                print('predict: ', predict)
                # print('candidate: ', candidate)


