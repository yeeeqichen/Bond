#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: EntityLinker.py
@time: 2020/8/11 5:16 下午
@desc:
"""
from Config import config, embed
from CandidateGenerator import get_candidates
from utils import merge_elements, get_mentions

NIL = 'fail to link: bond kind not found in knowledge base!'


# todo:相似度不够高时，进行消岐(长尾，因为需要用到正文信息）
def entity_linker(sentence, mentions, kinds, missing_element):
    """
    :param sentence: mention所在句子
    :param mentions: 句子中的mention
    :param missing_element: 是否是要素缺失的情况
    :return: 每个mention对应的entity
    """

    # 目前按照名称的相似度选择链接对象
    entity_set = []
    candidate_set = []
    for mention, kind, is_miss in zip(mentions, kinds, missing_element):
        if is_miss:
            entities = []
            # todo:补全要素后再进行链接
            # 目前思路：
            # article_blocks, elements = process_article(article)
            # if len(article_blocks) > 0: 正文中包含完整的债券名，那就直接用这个链接
            #   mention_set, kind_set, _ = get_mentions(article_blocks)
            #   for _mention, _kind in zip(mention_set, kind_set):
            #        ...
            #         entities.append(...)
            # else:
            #   补要素
            entity_set.append(entities)
            candidate_set.append([])
            continue
        if kind in config.bond_kind:
            kind_idx = config.bond_kind.index(kind)
        else:
            kind_idx = -1
        mention_embedding = embed(mention).numpy()
        top_n = get_candidates(mention_embedding, kind_idx)
        candidates = []
        for idx, sim in top_n:
            candidates.append((config.names[idx], sim))
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        entity_set.append(candidates[0][0][:-1])
        candidate_set.append(candidates)
    return candidate_set, entity_set


def link(text, tags):
    """
    :param text: 待链接的mention所在的文本
    :param tags: NER标注序列
    :return: text中的mention以及其对应的链接结果
    """
    blocks = merge_elements(text, tags)
    mention_set, kind_set, missing_element = get_mentions(blocks)
    if len(mention_set) == 0:
        yield 'no mention'
    else:
        candidates, predicts = entity_linker(text, mention_set, kind_set, missing_element)
        for mention, _, predict in zip(mention_set, candidates, predicts):
            yield {'mention': mention, 'predict': predict}
