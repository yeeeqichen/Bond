import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from Config import config


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
        best_score = sim_matrix[0][top_n_idx[0]]
        predict = top_n_idx[0]
        for idx in top_n_idx[1:]:
            if sim_matrix[0][idx] > best_score:
                predict = idx
                best_score = sim_matrix[0][idx]
        return top_n_idx, predict


candidate_generator = CandidateGenerator(config.full_embeddings, config.short_embeddings, config.top_k)



