# coding=UTF-8
"""
@description:
    该文件实现entity_linker()方法，用于预测句子中的mention对应的entity
    并封装了项目接口link（），接收文本和NER标签序列，返回text中所有mention以及其对应链接结果
    调用示例：for result in link(text, tags):
                 print(result)
@author: yeeeqichen
"""
from Config import config, embed
from CandidateGenerator import get_candidates
from Merge import merge_elements

NIL = 'fail to link: bond kind not found in knowledge base!'


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


# todo:相似度不够高时，进行消岐(长尾，因为需要用到正文信息）
def entity_linker(sentence, mentions, kinds):
    """
    :param sentence: mention所在句子
    :param mentions: 句子中的mention
    :return: 每个mention对应的entity
    """

    # 目前按照名称的相似度选择链接对象
    entity_set = []
    candidate_set = []
    for mention, kind in zip(mentions, kinds):
        if kind in config.bond_kind:
            kind_idx = config.bond_kind.index(kind)
        else:
            kind_idx = -1
        mention_embedding = embed(mention).numpy()
        # sentence_embedding = embed(sentence).numpy()
        # get candidates
        top_n = get_candidates(mention_embedding, kind_idx)
        # candidate_embeddings = []
        candidates = []
        for idx, sim in top_n:
            # candidate_embeddings.append(config.full_embeddings[idx])
            candidates.append((config.names[idx], sim))
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        entity_set.append(candidates[0][0])
        candidate_set.append(candidates)
    return candidate_set, entity_set


def link(text, tags):
    """
    :param text: 待链接的mention所在的文本
    :param tags: NER标注序列
    :return: text中的mention以及其对应的链接结果
    """
    blocks = merge_elements(text, tags)
    mention_set, kind_set = get_mentions(blocks)
    if len(mention_set) == 0:
        return 'no mention'
    candidates, predicts = entity_linker(text, mention_set, kind_set)
    for mention, _, predict in zip(mention_set, candidates, predicts):
        yield {'mention': mention, 'predict': predict[:-1]}
