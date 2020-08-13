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

NIL = 'fail to link: bond kind not found in knowledge base!'


# 目前实现的效果：不缺要素直接链接，缺要素的话就到正文里找有没有不缺要素的，找到就用这些链接，todo：没找到怎么处理
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
        _mention_embed = embed(_m).numpy()
        _top_n = get_candidates(_mention_embed, _kind_idx)
        for idx, sim in _top_n:
            _candidates.append((config.names[idx], sim))
        _candidates = sorted(_candidates, key=lambda x: x[1], reverse=True)
        return _candidates, _candidates[0][0][:-1]
    # 目前按照名称的相似度选择链接对象

    title_blocks = merge_elements(title, title_tags)
    title_mentions, title_kinds, title_missing = get_mentions(title_blocks)
    entity_set = []
    candidate_set = []
    for title_mention, title_kind, is_miss, title_block in \
            zip(title_mentions, title_kinds, title_missing, title_blocks):
        linking_result = []
        candidates = []
        if is_miss:
            # 缺失要素的情况就去处理原文
            print('missing element!')
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
            if len(article_blocks) > 0:
                article_mentions, article_kinds, _ = get_mentions(article_blocks)
                for article_mention, article_kind in zip(article_mentions, article_kinds):
                    print('mentions in article: ', article_mention)
                    _candi, predict = _predict(article_mention, article_kind)
                    linking_result.append(predict)
                    candidates.append(_candi)
                linking_result = list(set(list(linking_result)))
            else:
                if '发债方' not in title_block['tags'] and '发债方' in article_elements and len(article_elements['发债方']) > 0:
                    company = sorted(list(article_elements['发债方']), key=lambda x: len(x), reverse=True)[0]
                    pad_mention = company + title_mention
                    print('padded mention: ', pad_mention)
                    _candi, predict = _predict(pad_mention, title_kind)
                    linking_result.append(predict)
                    candidates.append(_candi)
                elif '资产证券化' in title_kind or '资产支持证券' in title_kind:
                    flag = False
                    pad = False
                    for ele, tag in zip(title_block['elements'], title_block['tags']):
                        if tag == '修饰语' and ('优' in ele or '次' in ele):
                            flag = True
                            break
                    if not flag:
                        for ele in list(article_elements['修饰语']):
                            if '优' in ele or '次' in ele:
                                pad = True
                                pad_mention = title_mention + ele
                                pad_mention += '资产支持证券' if '资产支持证券' not in pad_mention else ''
                                print('padded mention: ', pad_mention)
                                _candi, predict = _predict(pad_mention, title_kind)
                                linking_result.append(predict)
                                candidates.append(_candi)
                        # 有可能正文中也没有优先级这一要素
                        if not pad:
                            pad_mention = title_mention
                            print('padded mention: ', pad_mention)
                            _candi, predict = _predict(pad_mention, title_kind)
                            linking_result.append(predict)
                            candidates.append(_candi)
        else:
            _candi, predict = _predict(title_mention, title_kind)
            linking_result.append(predict)
            candidates.append(_candi)
        entity_set.append(linking_result)
        candidate_set.append(candidates)
    return title_mentions, candidate_set, entity_set


def link(_input):
    """
    :param _input: 文章解析得到的list
    :return: 链接结果，以 [{'mention': .., 'entity': ..}, ..]形式返回
    """
    title, title_tags, article = process_input(_input)
    mentions, _, entities = entity_linker(title, title_tags, article)
    result = []
    for mention, entity in zip(mentions, entities):
        dic = dict()
        dic['mention'] = mention
        dic['entity'] = ', '.join(entity)
        result.append(dic)
    return result, title, article

#
# def entity_linker_test(title, title_tags, article):
#     """
#     :param title: 标题
#     :param article: 正文,以段落的形式呈现（para， para_tags)
#     :param title_tags: 标题NER标注序列
#     :return: text中的mention以及其对应的链接结果
#     """
#     def _predict(_m, _k):
#         _candidates = []
#         if _k in config.bond_kind:
#             _kind_idx = config.bond_kind.index(_k)
#         else:
#             _kind_idx = -1
#         _mention_embed = embed(_m).numpy()
#         _top_n = get_candidates(_mention_embed, _kind_idx)
#         for idx, sim in _top_n:
#             _candidates.append((config.names[idx], sim))
#         _candidates = sorted(_candidates, key=lambda x: x[1], reverse=True)
#         return _candidates, _candidates[0][0][:-1]
#     # 目前按照名称的相似度选择链接对象
#
#     entity_set = []
#     candidate_set = []
#     article_blocks = []
#     title_mentions = []
#     article_elements = dict()
#     article_elements['年份'] = set()
#     article_elements['发债方'] = set()
#     article_elements['修饰语'] = set()
#     article_elements['期数'] = set()
#     article_elements['债券类型'] = set()
#     for para, para_tags in article:
#         _blocks, article_elements = process_articles(para, para_tags, article_elements)
#         article_blocks += _blocks
#     if len(article_blocks) > 0:
#         article_mentions, article_kinds, _ = get_mentions(article_blocks)
#         for article_mention, article_kind in zip(article_mentions, article_kinds):
#             print('mentions in article: ', article_mention)
#             _candi, predict = _predict(article_mention, article_kind)
#             title_mentions.append(article_mention)
#             candidate_set.append(_candi)
#             entity_set.append(predict)
#     return title_mentions, candidate_set, entity_set
#
#
# def link(_input):
#     """
#     :param _input: 文章解析得到的list
#     :return: 链接结果，以 [{'mention': .., 'entity': ..}, ..]形式返回
#     """
#     title, title_tags, article = process_input(_input)
#     mentions, _, entities = entity_linker(title, title_tags, article)
#     result = []
#     for mention, entity in zip(mentions, entities):
#         dic = dict()
#         dic['mention'] = mention
#         dic['entity'] = ', '.join(entity)
#         result.append(dic)
#     return result, title, article
#
#
# def link_for_test(_input):
#     """
#     :param _input: 文章解析得到的list
#     :return: 链接结果，以 [{'mention': .., 'entity': ..}, ..]形式返回
#     """
#     title, title_tags, article = process_input(_input)
#     mentions, _, entities = entity_linker_test(title, title_tags, article)
#     result = []
#     for mention, entity in zip(mentions, entities):
#         dic = dict()
#         dic['mention'] = mention
#         dic['entity'] = ', '.join(entity)
#         result.append(dic)
#     return result, title, article
