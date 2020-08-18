#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: EntityLinker.py
@time: 2020/8/11 5:16 下午
@desc:
"""
from Config import config
from utils import merge_elements, get_mentions, process_articles, process_input, get_candidates

NIL = 'Fail to link: Bond not found in knowledge base!'


def pad_element(block, article_elements, mention):
    results = []
    new_block = dict(block)
    # pad_mention = title_mention
    if '期数' not in block['tags'] and len(article_elements['期数']) > 0:
        num = ""
        for _n in list(article_elements['期数']):
            if '期' in _n:
                num += _n
                break
        if len(num) > 0:
            new_block['tags'].insert(0, '期数')
            new_block['elements'].insert(0, num)
    if '年份' not in block['tags'] and len(article_elements['年份']) > 0:
        year = sorted(list(article_elements['年份']), key=lambda x: len(x))[0]
        if len(year) < 4:
            year = '20' + year
        if '年' not in year:
            year += '年'
        new_block['tags'].insert(0, '年份')
        new_block['elements'].insert(0, year)
    if '发债方' not in block['tags'] and len(article_elements['发债方']) > 0:
        company = sorted(list(article_elements['发债方']), key=lambda x: len(x), reverse=True)[0]
        new_block['tags'].insert(0, '发债方')
        new_block['elements'].insert(0, company)
    if '资产证券化' in mention or '资产支持' in mention or '专项计划' in mention:
        flag = False
        pad = False
        for ele, tag in zip(block['elements'], block['tags']):
            if tag == '修饰语' and ('优' in ele or '次' in ele):
                flag = True
                break
        if not flag:
            for ele in list(article_elements['修饰语']):
                if '优先' in ele or '次' in ele:
                    pad = True
                    _block = dict(new_block)
                    _block['tags'].append('修饰语')
                    _block['elements'].append(ele)
                    if '资产支持证券' not in mention:
                        _block['tags'].append('债券类型')
                        _block['elements'].append('资产支持证券')
                    results.append(_block)
            # 有可能正文中也没有优先级这一要素
            if not pad:
                results.append(new_block)
        else:
            results.append(new_block)
    else:
        results.append(new_block)
    return results

# 目前实现的效果：不缺要素直接链接，缺要素的话就到正文里找有没有不缺要素的，找到就用这些链接，没找到就用正文中的要素进行补全
def entity_linker_with_use(title, title_tags, article):
    """
    :param title: 标题
    :param article: 正文,以段落的形式呈现（para， para_tags)
    :param title_tags: 标题NER标注序列
    :return: text中的mention以及其对应的链接结果
    """
    def _predict(_m, _k):
        from Config import embed
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
                pad_results = pad_element(title_block, article_elements, title_mention)
                for block in pad_results:
                    pad_mention = ''
                    for ele in block['elements']:
                        pad_mention += ele
                    _candi, predict, score = _predict(pad_mention, title_kind)
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
        title_entity_set.append(linking_result)
        title_candidate_set.append(candidates)
        title_scores.append(scores)
    return title_mentions, title_candidate_set, title_entity_set, title_scores, \
        article_mentions, article_candidate_set, article_entity_set, article_scores


def entity_linker_with_elements(title, title_tags, article):
    def _predict(block):
        company = None
        kind = None
        year = None
        num = None
        for ele, tag in zip(block['elements'], block['tags']):
            if tag == '发债方':
                company = ele
            elif tag == '债券类型':
                kind = ele
            elif tag == '年份':
                if len(ele) > 4:
                    year = ele[:4]
                else:
                    year = ele
            elif tag == '期数':
                num = ele
                if ele[0] == '第' or ele[0] == '(' or ele[0] == '（':
                    num = num[1:]
                if ele[-1] == ')' or ele[-1] == '）':
                    num = num[:-1]
        # print(kind, company, year, num)
        temp_candidates = []
        if kind is not None and kind not in config.bond_kind:
            _candidates = []
        else:
            if kind is None:
                _candidates = config.bond_clusters[config.bond_kind.index('#')]
            else:
                _candidates = config.bond_clusters[config.bond_kind.index(kind)]
        if company is not None:
            for candi in _candidates:
                if company in candi:
                    temp_candidates.append(candi)
            _candidates = temp_candidates
            temp_candidates = []
        if year is not None:
            for candi in _candidates:
                if year in candi:
                    temp_candidates.append(candi)
            _candidates = temp_candidates
            temp_candidates = []
        if num is not None:
            for candi in _candidates:
                if num in candi:
                    temp_candidates.append(candi)
            _candidates = temp_candidates
            temp_candidates = []
    # 目前按照名称的相似度选择链接对象
        if len(_candidates) == 0:
            return NIL
        else:
            return _candidates[0]

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

    for title_mention, title_kind, is_miss, title_block in \
            zip(title_mentions, title_kinds, title_missing, title_blocks):
        linking_result = []
        candidates = []
        scores = []
        if is_miss:
            pad_blocks = pad_element(title_block, article_elements, title_mention)
            for block in pad_blocks:
                linking_result.append(_predict(block))
                scores.append(0)
                candidates.append([])
        else:
            linking_result.append(_predict(title_block))
            candidates.append([])
            scores.append(0)
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
    if config.use_USE:
        link_func = entity_linker_with_use
    else:
        link_func = entity_linker_with_elements
    title, title_tags, article = process_input(_input)
    title_mentions, _, title_entities, title_scores, article_mentions, _, article_entities, article_scores = \
        link_func(title, title_tags, article)
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
