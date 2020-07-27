from Config import config, embed
from CandidateGenerator import candidate_generator
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from Merge import merge_elements


# todo:相似度不够高时，进行消岐
def entity_linker(sentence, mentions):
    '''
    :param sentence: mention所在句子
    :param mentions: 句子中的mention
    :return: 每个mention对应的entity
    '''

    # 目前按照名称的相似度选择链接对象
    entity_set = []
    candidate_set = []
    for mention in mentions:
        mention_embedding = embed(mention).numpy()
        sentence_embedding = embed(sentence).numpy()
        # get candidates
        top_n_idx, predict = candidate_generator.get_candidates(mention_embedding, False)
        candidate_embeddings = []
        candidate_names = []
        for idx in top_n_idx:
            candidate_embeddings.append(config.full_embeddings[idx])
            candidate_names.append(config.names[idx])
        if predict is not None:
            entity_set.append(config.names[predict])
        else:
            pass
        candidate_set.append(candidate_names)
    return candidate_set, entity_set


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


