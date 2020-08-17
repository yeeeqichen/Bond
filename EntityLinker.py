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
from utils import merge_elements, get_mentions, process_articles, process_input, get_candidates

NIL = 'Fail to link: Bond not found in knowledge base!'


# 目前实现的效果：不缺要素直接链接，缺要素的话就到正文里找有没有不缺要素的，找到就用这些链接，没找到就用正文中的要素进行补全
def entity_linker(title, title_tags, article):
    """
    :param title: 标题
    :param article: 正文,以段落的形式呈现（para， para_tags)
    :param title_tags: 标题NER标注序列
    :return: text中的mention以及其对应的链接结果
    """
    def _predict(_m, _k):
        _candidates = []
        if _k in config.bond_kind:
            _kind_idx = config.bond_kind.index(_k)
        else:
            _kind_idx = -1
            for char in config.short_character:
                if char in _m:
                    _kind_idx = config.bond_kind.index(char)
                    break
        _mention_embed = embed(_m).numpy()
        _top_n = get_candidates(_mention_embed, _kind_idx)
        for idx, sim in _top_n:
            _candidates.append((config.names[idx], sim))
        _candidates = sorted(_candidates, key=lambda x: x[1], reverse=True)
        return _candidates, _candidates[0][0][:-1], _candidates[0][1]
    # 目前按照名称的相似度选择链接对象

    title_entity_set = []
    title_candidate_set = []
    title_scores = []
    article_entity_set = []
    article_candidate_set = []
    article_scores = []
    title_blocks = merge_elements(title, title_tags)
    title_mentions, title_kinds, title_missing = get_mentions(title_blocks)
    assert (len(title_mentions) == len(title_kinds))
    assert(len(title_kinds) == len(title_missing))
    article_blocks = []
    article_elements = dict()
    article_elements['年份'] = set()
    article_elements['发债方'] = set()
    article_elements['修饰语'] = set()
    article_elements['期数'] = set()
    article_elements['债券类型'] = set()
    for para, para_tags in article:
        _blocks, article_elements = process_articles(para, para_tags, article_elements)
        article_blocks += _blocks
    article_mentions, article_kinds, _ = get_mentions(article_blocks)
    assert (len(article_mentions) == len(article_kinds))
    for article_mention, article_kind in zip(article_mentions, article_kinds):
        _candi, predict, score = _predict(article_mention, article_kind)
        if score < config.thresh_hold:
            predict = NIL
        article_candidate_set.append(_candi)
        article_entity_set.append(predict)
        article_scores.append(score)
    bonds_in_article = list(set(article_entity_set))

    for title_mention, title_kind, is_miss, title_block in \
            zip(title_mentions, title_kinds, title_missing, title_blocks):
        linking_result = []
        candidates = []
        scores = []
        if is_miss:
            # 使用正文提及的债券
            # 由于补年份和期数的目前只能处理单个债券，因此有多只债券的放在这里处理
            if len(bonds_in_article) > 0 and ('年份' not in title_block['tags'] or '期数' not in title_block['tags']) \
                    and '资产支持' not in title_kind and '资产证券化' not in title_kind and '专项计划' not in title_kind:
                for bond in bonds_in_article:
                    flag = True
                    if '发债方' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('发债方')] not in bond:
                        flag = False
                    if '年份' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('年份')] not in bond:
                        flag = False
                    if '期数' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('期数')] not in bond:
                        flag = False
                    if '债券类型' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('债券类型')] not in bond:
                        flag = False
                    if flag:
                        linking_result.append(bond)
                if len(linking_result) == 0:
                    linking_result.append(NIL)
                    candidates.append([])
                    scores.append(0)
            # 补全要素
            else:
                if '资产证券化' in title_kind or '资产支持' in title_kind or '专项计划' in title_kind:
                    flag = False
                    pad = False
                    for ele, tag in zip(title_block['elements'], title_block['tags']):
                        if tag == '修饰语' and ('优' in ele or '次' in ele):
                            flag = True
                            break
                    if not flag:
                        for ele in list(article_elements['修饰语']):
                            if '优先' in ele or '次' in ele:
                                pad = True
                                pad_mention = title_mention + ele
                                pad_mention += '资产支持证券' if '资产支持证券' not in pad_mention else ''
                                # print('padded mention: ', pad_mention)
                                _candi, predict, score = _predict(pad_mention, title_kind)
                                if score < config.thresh_hold:
                                    predict = NIL
                                linking_result.append({"padded_mention": pad_mention, "entity": predict})
                                candidates.append(_candi)
                                scores.append(score)
                        # 有可能正文中也没有优先级这一要素
                        if not pad:
                            _candi, predict, score = _predict(title_mention, title_kind)
                            if score < config.thresh_hold:
                                predict = NIL
                            linking_result.append(predict)
                            candidates.append(_candi)
                            scores.append(score)
                    else:
                        _candi, predict, score = _predict(title_mention, title_kind)
                        if score < config.thresh_hold:
                            predict = NIL
                        linking_result.append(predict)
                        candidates.append(_candi)
                        scores.append(score)
                else:
                    pad_mention = title_mention
                    if '发债方' not in title_block['tags'] and len(article_elements['发债方']) > 0:
                        company = sorted(list(article_elements['发债方']), key=lambda x: len(x), reverse=True)[0]
                        pad_mention = company + pad_mention
                    if '期数' not in title_block['tags'] and len(article_elements['期数']) > 0:
                        num = ""
                        for _n in list(article_elements['期数']):
                            if '期' in _n:
                                num += _n
                                break
                        pad_mention = pad_mention + num
                    if '年份' not in title_block['tags'] and len(article_elements['年份']) > 0:
                        num = sorted(list(article_elements['年份']), key=lambda x: len(x))[0]
                        if len(num) < 4:
                            num = '20' + num
                        if '年' not in num:
                            num += '年'
                        pad_mention = num + pad_mention
                    # print('padded mention: ', pad_mention)
                    _candi, predict, score = _predict(pad_mention, title_kind)
                    if score < config.thresh_hold:
                        predict = NIL
                    linking_result.append({"padded_mention": pad_mention, "entity": predict})
                    candidates.append(_candi)
                    scores.append(score)
        else:
            _candi, predict, score = _predict(title_mention, title_kind)
            if score < config.thresh_hold:
                predict = NIL
            linking_result.append(predict)
            candidates.append(_candi)
            scores.append(score)
        title_entity_set.append(linking_result)
        title_candidate_set.append(candidates)
        title_scores.append(scores)
    return title_mentions, title_candidate_set, title_entity_set, title_scores, \
        article_mentions, article_candidate_set, article_entity_set, article_scores


def link(_input):
    """
    :param _input: 文章解析得到的list
    :return: 链接结果，以 [{'mention': .., 'entity': ..}, ..]形式返回
    """
    title, title_tags, article = process_input(_input)
    title_mentions, _, title_entities, title_scores, article_mentions, _, article_entities, article_scores = \
        entity_linker(title, title_tags, article)
    title_result = []
    article_result = []
    for mention, entity, score in zip(title_mentions, title_entities, title_scores):
        dic = dict()
        dic['mention'] = mention
        dic['entity'] = entity
        dic['score'] = score
        title_result.append(dic)
    for mention, entity, score in zip(article_mentions, article_entities, article_scores):
        dic = dict()
        dic['mention'] = mention
        dic['entity'] = entity
        dic['score'] = score
        article_result.append(dic)
    return title_result, article_result, title, article
