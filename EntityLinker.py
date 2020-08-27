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
from utils import merge_elements, get_mentions, process_paragraph, process_input, pad_element

NIL = 'Fail to link: Bond not found in knowledge base!'


def entity_linker_with_use(title, title_tags, article):
    """
    :param title: 标题
    :param article: 正文,以段落的形式呈现（para， para_tags)
    :param title_tags: 标题NER标注序列
    :return: text中的mention以及其对应的链接结果
    """
    from Config import embed

    def _predict(_m, _k, _backup):
        """
        :param _m: 待预测的mention
        :param _k: 待预测的债券类型
        :param _backup: 使用映射表将简称转换为全称后的mention
        :return: 候选， 链接结果，链接得分（距离）
        """
        def _find_neighbor(_mention):
            """
            :param _mention: 用于寻找近邻的mention
            :return: 近邻的距离，近邻的索引（债券名库中）
            """
            nonlocal _flag
            nonlocal neighbor_finder
            _embed = embed(_mention).numpy()
            _distance, _idx = neighbor_finder.query(_embed, k=1)
            if _flag:
                new_embed = embed(_mention + '资产支持证券').numpy()
                new_distance, new_idx = neighbor_finder.query(new_embed, k=1)
                if new_distance < _distance:
                    _distance = new_distance
                    _idx = new_idx
            return _distance, _idx

        _flag = False
        if '资产支持证券' in _m:
            _flag = True
        _candidates = []
        if _k in config.bond_kind:
            _kind_idx = config.bond_kind.index(_k)
        else:
            _kind_idx = -1
            for char in config.short_character:
                if char in _m:
                    _kind_idx = config.bond_kind.index(char)
                    break
        if _kind_idx == -1:
            neighbor_finder = config.total_neighbor
        else:
            neighbor_finder = config.neighbor_in_cluster[_kind_idx]
        distance, idx = _find_neighbor(_m)
        if _backup is not None:
            backup_distance, backup_idx = _find_neighbor(_backup)
            if backup_distance < distance:
                distance = backup_distance
                idx = backup_idx
        if _kind_idx == -1:
            return [], config.names[config.full_to_id[idx[0][0]]][:-1], distance
        return [], config.names[config.cluster_to_id[_kind_idx][idx[0][0]]][:-1], distance

    def _get_backup(_block):
        """
        :param _block: 债券要素块
        :return: 将简称映射为全称后的债券mention
        """
        _backup = None
        if '发债方' in _block['tags']:
            idx = _block['tags'].index('发债方')
            if _block['elements'][idx] in config.map_table:
                _backup = ''
                for i, ele in enumerate(_block['elements']):
                    if i == idx:
                        _backup += config.map_table[ele]
                    else:
                        _backup += ele
        return _backup
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
        _blocks, article_elements = process_paragraph(para, para_tags, article_elements)
        article_blocks += _blocks
    article_mentions, article_kinds, _ = get_mentions(article_blocks)
    assert (len(article_mentions) == len(article_kinds))
    for article_mention, article_kind, article_block in zip(article_mentions, article_kinds, article_blocks):
        _candi, predict, score = _predict(article_mention, article_kind, _get_backup(article_block))
        article_candidate_set.append(_candi)
        article_entity_set.append(predict)
        article_scores.append(score)
    bonds_in_article = list(set(article_entity_set))
    # 这一步是为了保证去重后顺序不变
    bonds_in_article.sort(key=article_entity_set.index)
    for title_mention, title_kind, is_miss, title_block in \
            zip(title_mentions, title_kinds, title_missing, title_blocks):
        linking_result = []
        candidates = []
        scores = []
        if is_miss:
            # 使用正文提及的债券，并保证发债方、年份、期数、债券类型一致
            if len(bonds_in_article) > 0 and ('年份' not in title_block['tags'] or '期数' not in title_block['tags']) \
                    and '资产支持' not in title_kind and '资产证券化' not in title_kind and '专项计划' not in title_kind:
                for bond in bonds_in_article:
                    flag = True
                    if flag and '发债方' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('发债方')] not in bond:
                        flag = False
                    if flag and '年份' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('年份')] not in bond:
                        flag = False
                    if flag and '期数' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('期数')] not in bond:
                        flag = False
                    if flag and '债券类型' in title_block['tags'] and \
                            title_block['elements'][title_block['tags'].index('债券类型')] not in bond:
                        flag = False
                    if flag:
                        linking_result.append(bond)
                if len(linking_result) == 0:
                    linking_result.append('')
                    candidates.append([])
                    scores.append(0)
            # 补全要素
            else:
                pad_results = pad_element(title_block, article_elements, title_mention)
                for block in pad_results:
                    pad_mention = ''
                    for ele in block['elements']:
                        pad_mention += ele
                    # print('pad mention:', pad_mention)
                    _candi, predict, score = _predict(pad_mention, title_kind, _get_backup(block))
                    linking_result.append(predict)
                    candidates.append(_candi)
                    scores.append(score)
        else:
            _candi, predict, score = _predict(title_mention, title_kind, _get_backup(title_block))
            linking_result.append(predict)
            candidates.append(_candi)
            scores.append(score)
        title_entity_set.append(list(set(linking_result)))
        title_candidate_set.append(candidates)
        title_scores.append(scores)
    return title_mentions, title_candidate_set, title_entity_set, title_scores, \
        article_mentions, article_candidate_set, article_entity_set, article_scores


def entity_linker_with_elements(title, title_tags, article):
    def _predict(_block):
        company = None
        kind = None
        year = None
        num = None
        _mention = ''
        for ele, tag in zip(_block['elements'], _block['tags']):
            _mention += ele
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
            _candidates = config.bond_clusters[config.bond_kind.index('#')]
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
            return NIL, _mention
        else:
            diff = 1e10
            _pre = None
            for _candi in _candidates:
                if abs(len(_mention) - len(_candi)) < diff:
                    _pre = _candi
                    diff = abs(len(_mention) - len(_candi))
            return _pre, _mention

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
        _blocks, article_elements = process_paragraph(para, para_tags, article_elements)
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
                predict, pad_mention = _predict(block)
                linking_result.append(predict)
                scores.append(0)
                candidates.append([])
        else:
            linking_result.append(_predict(title_block)[0])
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
    title, title_tags, article = process_input(_input, config.is_news)
    title_mentions, _, title_entities, title_scores, article_mentions, _, article_entities, article_scores = \
        link_func(title, title_tags, article)
    title_result = []
    article_result = []
    for mention, entity, score in zip(title_mentions, title_entities, title_scores):
        dic = dict()
        dic['mention'] = mention
        dic['entity'] = entity
        # dic['score'] = score
        title_result.append(dic)
    for mention, entity, score in zip(article_mentions, article_entities, article_scores):
        dic = dict()
        dic['mention'] = mention
        dic['entity'] = entity
        # dic['score'] = score
        article_result.append(dic)
    return title_result, article_result, title, article
