from Config import config, embed
from CandidateGenerator import get_candidates

NIL = 'fail to link: bond kind not found in knowledge base!'


# def get_mention_kind(mention):
#     kind_idx = 0
#     for idx, kind in enumerate(config.bond_kind):
#         if kind in mention or kind == '#':
#             kind_idx = idx
#             break
#     return kind_idx


# todo:相似度不够高时，进行消岐(长尾，因为需要用到正文信息）
def entity_linker(sentence, mentions, kinds):
    '''
    :param sentence: mention所在句子
    :param mentions: 句子中的mention
    :return: 每个mention对应的entity
    '''

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