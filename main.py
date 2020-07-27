from Config import config
from EntityLinker import entity_linker
import json
from Merge import merge_elements


def get_mentions(_blocks):
    _mentions = []
    for block in _blocks:
        mention = ''
        for ele in block['elements']:
            mention += ele
        _mentions.append(mention)
    return _mentions


if __name__ == '__main__':
    texts = []
    tags = []
    with open(config.labeled_text) as f:
        for line in f:
            dic = json.loads(line)
            texts.append(dic['text'])
            tags.append(dic['tags'])

    for text, tags in zip(texts, tags):
        blocks = merge_elements(text, tags)
        mention_set = get_mentions(blocks)
        candidates, predicts = entity_linker(text, mention_set)
        print('text: ', text)
        for mention, candidate, predict in zip(mention_set, candidates, predicts):
            print('mention: ', mention)
            print('predict: ', predict)
            print('candidate: ', candidate)


