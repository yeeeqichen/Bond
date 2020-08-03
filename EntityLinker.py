# coding=UTF-8
"""
@description:
    该文件对外提供entity_linker()方法，用于预测句子中的mention对应的entity
@author: yeeeqichen
"""
from Config import config, embed
from CandidateGenerator import get_candidates

NIL = 'fail to link: bond kind not found in knowledge base!'


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