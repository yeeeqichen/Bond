from Config import config, embed
from CandidateGenerator import candidate_generator


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