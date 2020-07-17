from Config import config, embed
from CandidateGenerator import candidate_generator
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def entity_linker(sentence, mentions):
    '''
    :param sentence: mention所在句子
    :param mentions: 句子中的mention
    :return: 每个mention对应的entity
    '''
    entity = []
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
        # disambiguation
        # sim_matrix = cosine_similarity(sentence_embedding, candidate_embeddings)
        # predict = top_n_idx[np.argmax(sim_matrix[0])]
        # entity.append((predict, config.names[predict]))
        entity.append(config.names[predict])
    return candidate_names, entity


sentences = ["河北银行股份有限公司关于发行绿色金融债券董事会决议2018年一期",
             "河北省地方政府债券招投标书(一般债券)2020年五期",
             "江苏银行次级债券发行结果公告2009年"]
mentions = [["河北银行股份有限公司绿色金融债券"],
            ["河北省地方政府债券一般债券"],
            ["江苏银行次级债券"]]

for sentence, mention in zip(sentences, mentions):
    candidates, entity = entity_linker(sentence, mention)
    for candidate in candidates:
        print(candidate)
    print(entity)

