import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from Config import config


# 返回候选集，若相似度大于一定阈值，直接给出链接结果
class CandidateGenerator:
    def __init__(self, full_embeddings, short_embeddings, top_k):
        self.full_embeddings = full_embeddings
        self.short_embeddings = short_embeddings
        self.top_k = top_k

    def get_candidates(self, mention_embedding, is_short):
        if not is_short:
            sim_matrix = cosine_similarity(mention_embedding, self.full_embeddings)
        else:
            sim_matrix = cosine_similarity(mention_embedding, self.short_embeddings)
        top_n_idx = np.argpartition(sim_matrix[0], -self.top_k)[-self.top_k:]
        best_score = sim_matrix[0][top_n_idx[-1]]
        if best_score >= config.thresh_hold:
            return top_n_idx, top_n_idx[-1]
        return top_n_idx, None


candidate_generator = CandidateGenerator(config.full_embeddings, config.short_embeddings, config.top_k)



