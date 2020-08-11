#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: utils.py
@time: 2020/8/11 5:16 下午
@desc:
"""

digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
reverse_digit = ['#', '一', '二', '三', '四', '五', '六', '七', '八', '九']


def process_articles(article):
    tags = []
    text = ""
    for ele in article:
        tags += ele['bond_arg']
        text += ele['text']
    temp_blocks = merge_elements(text, tags)
    article_blocks = []
    elements = dict()
    elements['年份'] = set()
    elements['发债方'] = set()
    elements['修饰语'] = set()
    elements['期数'] = set()
    elements['债券类型'] = set()
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
    for block in _blocks:
        mention = ''
        flag = 0
        if '发债方' not in block['tags'] or ('年份' not in block['tags'] and '期数' not in block['tags']):
            _missing_element.append(True)
        else:
            _missing_element.append(False)
        for ele, kind in zip(block['elements'], block['tags']):
            mention += ele
            if kind == '债券类型':
                _bond_kinds.append(ele)
                flag = 1
        _mentions.append(mention)
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


def add_elements_to_blocks(text, article, blocks):
    # 获得正文的债券，只取不缺要素的，并获取正文中的要素集合，用于后续要素的补全
    article_blocks, article_elements = process_articles(article)

# article = [{"bond_arg": ["B-发债方", "I-发债方", "I-发债方", "I-发债方", "O", "O", "O", "O", "O", "B-债券类型", "I-债券类型", "I-债券类型", "I-债券类型", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": "title", "pos": "title", "text": "宝龙实业：10亿元公司债券票面利率确定为6.50%", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 0, "pos": 0, "text": "来源：中国网地产", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "I-发债方", "B-年份", "I-年份", "I-年份", "I-年份", "I-年份", "B-修饰语", "I-修饰语", "I-修饰语", "I-修饰语", "B-修饰语", "I-修饰语", "I-修饰语", "I-修饰语", "B-债券类型", "I-债券类型", "I-债券类型", "I-债券类型", "I-债券类型", "I-债券类型", "B-期数", "I-期数", "I-期数", "I-期数", "I-期数", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 1, "pos": 1, "text": "中国网地产讯 8月6日，据深交所消息，上海宝龙实业发展（集团）有限公司2020年公开发行住房租赁专项公司债券（第二期）票面利率确定为6.50%。", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 2, "pos": 2, "text": "消息显示，本期债券发行规模不超过10亿元（含），票面利率询价区间为5.0%-6.8%，发行期限为3年，附第2年末发行人调整票面利率选择权和投资者回售选择权。", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "B-年份", "I-年份", "B-发债方", "I-发债方", "B-期数", "I-期数", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 2, "pos": 3, "text": "债券简称20宝龙04，债券代码149194。", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 3, "pos": 4, "text": "债券牵头主承销商、簿记管理人、债券受托管理人为中金公司，联席主承销商为中信证券。", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 3, "pos": 5, "text": "起息日为2020年8月7日。", "type": "text"}, {"bond_arg": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "paragraph": 4, "pos": 6, "text": "据悉，本期债券募集资金中70%拟用于公司住房租赁项目建设（包括置换前期的建安投入以及相关借款），剩余部分拟用于补充公司营运资金。", "type": "text"}]
# print(process_articles(article))




