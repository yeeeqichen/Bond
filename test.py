from CandidateGenerator import candidate_generator
from sys import argv
from Config import config, embed

sentence = argv[1]
is_short = argv[2] == 'short'
sentence_embedding = embed(sentence).numpy()
top_n_idx, predict = candidate_generator.get_candidates(sentence_embedding, is_short)
for idx in top_n_idx:
    print(config.names[idx])
print(config.names[predict])
