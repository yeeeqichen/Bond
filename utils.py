#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: utils.py
@time: 2020/8/11 5:16 下午
@desc:
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from Config import config
digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
reverse_digit = ['#', '一', '二', '三', '四', '五', '六', '七', '八', '九']


def process_input(_input):
    title = ''
    article = []
    title_tags = []
    cur_para = 2
    para = ''
    para_tags = []
    for obj in _input:
        if obj['type'] != 'text':
            continue
        if obj['paragraph'] == 'title':
            continue
        if int(obj['paragraph']) < 2:
            title += obj['text']
            title_tags += obj['bond_arg']
        else:
            if int(obj['paragraph']) == cur_para:
                para += obj['text']
                para_tags += obj['bond_arg']
            else:
                article.append((para, para_tags))
                cur_para = int(obj['paragraph'])
                para = ''
                para_tags = []
                para += obj['text']
                para_tags += obj['bond_arg']
    if len(para) > 0:
        article.append((para, para_tags))
    return title, title_tags, article


def process_articles(article, article_tags, elements):
    if article is None:
        return [], dict()
    temp_blocks = merge_elements(article, article_tags)
    article_blocks = []
    for block in temp_blocks:
        if '年份' in block['tags'] and '期数' in block['tags'] and '发债方' in block['tags']:
            article_blocks.append(block)
        for idx, tag in enumerate(block['tags']):
            elements[tag].add(block['elements'][idx])
    return article_blocks, elements


def get_mentions(_blocks):
    """
    :param _blocks:每个block表示一只债券
    :return: 每只债券的mention，及其对应的债券类型，如果没有则返回 #
    """
    _mentions = []
    _bond_kinds = []
    _missing_element = []
    special_pattern = ['资产支持证券', '专项计划', '资产证券化']
    for block in _blocks:
        mention = ''
        flag = 0
        if '发债方' not in block['tags'] or '年份' not in block['tags'] or '期数' not in block['tags']:
            _missing_element.append(True)
        elif '债券类型' in block['tags']:
            _flag = 0
            for pattern in special_pattern:
                if pattern in block['elements'][block['tags'].index('债券类型')]:
                    _flag = 1
                    break
            if _flag:
                _missing_element.append(True)
            else:
                _missing_element.append(False)
        else:
            _missing_element.append(False)
        # assert(len(block['elements']) == len(block['tags']))
        for ele, kind in zip(block['elements'], block['tags']):
            mention += ele
            if kind == '债券类型':
                _bond_kinds.append(ele)
                flag = 1
        _mentions.append(mention)
        # 考虑到可能出现缩写里面将债券类型（字母）标错，这里抢救一下
        if flag == 0:
            for k in config.bond_kind:
                if k in mention:
                    _bond_kinds.append(k)
                    flag = 1
                    break
            if flag == 0:
                _bond_kinds.append('#')
    return _mentions, _bond_kinds, _missing_element


# 将中文转数字
def _trans(s):
    num = 0
    if s:
        idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
        if idx_q != -1:
            num += digit[s[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[s[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # 十前忽略一的处理
            num += digit.get(s[idx_s - 1:idx_s], 1) * 10
        if s[-1] in digit:
            num += digit[s[-1]]
    return num


# 将数字转中文
def _reverse_trans(num):
    s = ''
    temp = []
    while num > 0:
        temp.append(num % 10)
        num = int(num / 10)
    temp.reverse()
    if len(temp) == 3:
        s += reverse_digit[temp[0]]
        s += '百'
        s += reverse_digit[temp[1]]
        s += '十'
        if temp[2] > 0:
            s += reverse_digit[temp[2]]
    elif len(temp) == 2:
        if temp[0] > 1:
            s += reverse_digit[temp[0]]
        s += '十'
        if temp[1] > 0:
            s += reverse_digit[temp[1]]
    else:
        s += reverse_digit[temp[0]]
    return s


def merge_elements(text, tags):
    """
    :param text:文本
    :param tags: NER识别的标签
    :return: 文本中的债券，以{'elements':['11', '青岛', '债', '01'], 'tags':['年份', '发债主体','债券类型', '期数']}形式表现
    """
    # 将形如 2015-2018年度 001-008期 第一期至第二十期 展开为多只债券
    def _decode_range():
        nonlocal blocks
        flag = 0
        for idx1 in range(len(blocks)):
            chinese = False
            for idx2, t in enumerate(blocks[idx1]['tags']):
                # 定位到具有年份或期数范围的债券
                if t == '年份' or t == '期数':
                    if('-' in blocks[idx1]['elements'][idx2] or '至' in blocks[idx1]['elements'][idx2]
                            or '~' in blocks[idx1]['elements'][idx2]):
                        flag = 1
                        span = blocks[idx1]['elements'][idx2]
                        # 下面计算出各个元素的范围
                        # i1、i2表示前一个数字的范围
                        i1 = 0
                        while span[i1] not in numbers:
                            i1 += 1
                        if span[i1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            chinese = True
                        if t == '年份' and chinese:
                            break
                        # j表示 两个数字的分割位置
                        j = span.find('-')
                        if j == -1:
                            j = span.find('至')
                            if j == -1:
                                j = span.find('~')
                        i2 = j - 1
                        while span[i2] not in numbers:
                            i2 -= 1
                        # k2、k1表示后一个数字的范围
                        k1 = len(span) - 1
                        while span[k1] not in numbers:
                            k1 -= 1
                        k2 = j + 1
                        while span[k2] not in numbers:
                            k2 += 1

                        # head为前缀、begin为第一个数字、end为第二个数字、tail是后缀
                        head = span[:i1]
                        begin = span[i1:i2 + 1]
                        end = span[k2:k1 + 1]
                        tail = span[k1 + 1:]
                        # 原地修改为范围的起始处，剩余的用于构造新的债券名
                        blocks[idx1]['elements'][idx2] = head + begin + tail
                        # 若数字是中文格式，需要进行转换
                        if chinese:
                            num1 = _trans(begin)
                            num2 = _trans(end)
                        else:
                            num1 = int(begin)
                            num2 = int(end)
                        length = len(begin)
                        # 将范围进行展开
                        for y in range(num1 + 1, num2 + 1):
                            temp = dict()
                            temp['elements'] = []
                            for e in blocks[idx1]['elements']:
                                temp['elements'].append(e)
                            temp['tags'] = blocks[idx1]['tags']
                            # 根据需要转化为中文表示，例如第一期
                            if chinese:
                                temp['elements'][idx2] = head + _reverse_trans(y) + tail
                            else:
                                temp['elements'][idx2] = head + str(y).zfill(length) + tail
                            blocks.append(temp)
                    # 处理第一期和第二期，第一期与第二期，2019年和2020年这样的情况
                    elif '和' in blocks[idx1]['elements'][idx2] or '与' in blocks[idx1]['elements'][idx2]:
                        span = blocks[idx1]['elements'][idx2]
                        j = span.find('和')
                        if j == -1:
                            j = span.find('与')
                        fir = span[:j]
                        sec = span[j + 1:]
                        blocks[idx1]['elements'][idx2] = fir
                        temp = dict()
                        temp['elements'] = []
                        temp['tags'] = blocks[idx1]['tags']
                        for e in blocks[idx1]['elements']:
                            temp['elements'].append(e)
                        temp['elements'][idx2] = sec
                        blocks.append(temp)

        return flag == 1

    idx = 0
    blocks = []
    block = dict()
    block['elements'] = []
    block['tags'] = []
    last_tag = ''
    special_mode = False
    # 用于缓存并列的多只债券
    queue = []
    while idx < len(tags):
        if 'B' in tags[idx]:
            # 抽取出元素标签和元素的值
            tag = tags[idx][2:]
            ele = text[idx]
            idx += 1
            while idx < len(tags) and 'I' in tags[idx]:
                ele += text[idx]
                idx += 1
            # 特殊模式指的是目前元素属于多个债券，例如2018年第一期、第二期xxx
            if special_mode:
                temp = queue[-1]
                # 对应于三个及三个以上并列的情况
                if (tag == '期数' and last_tag == '期数') or (tag == '年份' and last_tag == '年份') or \
                        (tag == '发债方' and last_tag == '发债方') or (tag == '债券类型' and last_tag == '债券类型'):
                    dic = dict()
                    dic['elements'] = []
                    dic['tags'] = []
                    for i in range(len(temp['tags']) - 1):
                        dic['elements'].append(temp['elements'][i])
                        dic['tags'].append(temp['tags'][i])
                    dic['elements'].append(ele)
                    dic['tags'].append(tag)
                    queue.append(dic)
                # 新的债券名的开始
                elif tag != '修饰语' and tag in temp['tags']:
                    special_mode = False
                    for b in queue:
                        blocks.append(b)
                    queue.clear()
                    block = dict()
                    block['elements'] = [ele]
                    block['tags'] = [tag]
                # 当前并列的债券所共同具有的要素
                else:
                    for b in queue:
                        b['elements'].append(ele)
                        b['tags'].append(tag)

            # 正常模式，处理单个债券
            else:
                # 进入特殊模式
                if (tag == '期数' and last_tag == '期数') or (tag == '年份' and last_tag == '年份') or \
                        (tag == '发债方' and last_tag == '发债方') or (tag == '债券类型' and last_tag == '债券类型'):
                    special_mode = True
                    queue.clear()
                    queue.append(block)
                    dic = dict()
                    dic['elements'] = []
                    dic['tags'] = []
                    for i in range(len(block['tags']) - 1):
                        dic['elements'].append(block['elements'][i])
                        dic['tags'].append(block['tags'][i])
                    dic['elements'].append(ele)
                    dic['tags'].append(tag)
                    queue.append(dic)
                # 新的债券名的开始
                elif tag != '修饰语' and tag in block['tags']:
                    blocks.append(block)
                    block = dict()
                    block['elements'] = [ele]
                    block['tags'] = [tag]
                # 将此要素加入到当前要素块中
                else:
                    block['elements'].append(ele)
                    block['tags'].append(tag)
            # 记录上一轮的标签情况，目前逻辑是连续出现两个期数或年份或发债方呢则进入特殊模式（多只债券并列）
            last_tag = tag
        else:
            idx += 1
    if special_mode:
        for b in queue:
            blocks.append(b)
    elif len(block['elements']) > 0:
        blocks.append(block)
    # 检查每支债券的元素，是否出现年份是范围或者期数是范围，如果有则对其进行展开
    _decode_range()
    return blocks


def get_candidates(mention_embedding, kind_idx):
    """
    :param mention_embedding:每个mention的embedding
    :param kind_idx: 每个mention的债券类型
    :return: 候选的债券索引及其相似度得分
    """
    # 在对应债券种类集合中选取相似度top k
    if kind_idx == -1 or len(config.bond_clusters[kind_idx]) == 0:
        sim_matrix = cosine_similarity(mention_embedding, config.full_embeddings)
        top_k = min(config.top_k, len(sim_matrix[0]))
        top_n = []
        temp_idx = np.argpartition(sim_matrix[0], -top_k)[-top_k:]
        # 转化为到债券名库（去除了英文债券）中的索引，原索引拆分了债券别名
        for idx in temp_idx:
            top_n.append((config.full_to_id[idx], sim_matrix[0][idx]))
    else:
        sim_matrix = cosine_similarity(mention_embedding, config.bond_clusters[kind_idx])
        top_k = min(config.top_k, len(sim_matrix[0]))
        temp_idx = np.argpartition(sim_matrix[0], -top_k)[-top_k:]
        # 转化为债券名库(去除了英文债券)中的索引,原索引是cluster内的索引
        top_n = []
        for idx in temp_idx:
            top_n.append((config.cluster_to_id[kind_idx][idx], sim_matrix[0][idx]))
        # 返回索引以及对应的相似度得分
    return top_n


# device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
# def _cosine_similarity(_mention, _cluster):
#     _mention = np.array(_mention)
#     _cluster = np.array(_cluster)
#     _mention_tensor = torch.from_numpy(_mention).to(device)
#     _mention_tensor_T = torch.from_numpy(_mention.T).to(device)
#     _cluster_tensor = torch.from_numpy(_cluster).to(device)
#     _cluster_tensor_T = torch.from_numpy(_cluster.T).to(device)
#     mat1 = torch.matmul(_mention_tensor, _mention_tensor_T).cpu()
#     mat2 = torch.matmul(_cluster_tensor, _cluster_tensor_T).cpu()
#     mat3 = torch.matmul(_mention_tensor, _cluster_tensor_T).cpu()
#     return mat3.numpy() / (np.sqrt(mat1.numpy()) * np.sqrt(np.diagonal(mat2.numpy())))


