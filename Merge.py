import json

digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
reverse_digit = ['#', '一', '二', '三', '四', '五', '六', '七', '八', '九']


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
    # 将形如 2015-2018年度 001-008期 第一期至第二十期 展开为多只债券
    def _decode_range():
        nonlocal blocks
        flag = 0
        for idx1 in range(len(blocks)):
            chinese = False
            for idx2, t in enumerate(blocks[idx1]['tags']):
                # 定位到具有年份或期数范围的债券
                if (t == '年份' or t == '期数') and \
                        ('-' in blocks[idx1]['elements'][idx2] or '至' in blocks[idx1]['elements'][idx2]):
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
                        if chinese:
                            temp['elements'][idx2] = head + _reverse_trans(y) + tail
                        else:
                            temp['elements'][idx2] = head + str(y).zfill(length) + tail
                        blocks.append(temp)
        return flag == 1

    idx = 0
    blocks = []
    block = dict()
    block['elements'] = []
    block['tags'] = []
    last_tag = ''
    special_mode = False
    # 用于缓存目前并列的多只债券
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
                if (tag == '期数' and last_tag == '期数') or (tag == '年份' and last_tag == '年份'):
                    dic = dict()
                    dic['elements'] = []
                    dic['tags'] = []
                    for i in range(len(temp['tags']) - 1):
                        dic['elements'].append(temp['elements'][i])
                        dic['tags'].append(temp['tags'][i])
                    dic['elements'].append(ele)
                    dic['tags'].append(tag)
                    queue.append(dic)
                elif tag != '修饰语' and tag in temp['tags']:
                    special_mode = False
                    for b in queue:
                        blocks.append(b)
                    queue.clear()
                    block = dict()
                    block['elements'] = [ele]
                    block['tags'] = [tag]
                else:
                    for b in queue:
                        b['elements'].append(ele)
                        b['tags'].append(tag)

            # 正常模式，处理单个债券
            else:
                # 如果要素不是修饰词并且要素已经在当前block中出现，我们认为这是一支新的债券（要素并列的情况后处理）
                if (tag == '期数' and last_tag == '期数') or (tag == '年份' and last_tag == '年份'):
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

                elif tag != '修饰语' and tag in block['tags']:
                    blocks.append(block)
                    block = dict()
                    block['elements'] = [ele]
                    block['tags'] = [tag]
                # 将此要素加入到当前要素块中
                else:
                    block['elements'].append(ele)
                    block['tags'].append(tag)

            # 记录上一轮的标签情况，目前逻辑是连续出现两个期数或年份呢则进入特殊模式，
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


if __name__ == '__main__':
    # path = '/Users/maac/Desktop/债券实体链接/hand_labeled.json'
    # with open(path) as f:
    #     for line in f:
    #         dic = json.loads(line)
    #         print(merge_elements(dic['text'], dic['tags']))
    text = '19呵呵第一至十一期xxx债券'
    tags = ['B-年份', 'I-年份', 'B-发债方', 'I-发债方', 'B-期数', 'I-期数','I-期数', 'I-期数', 'I-期数', 'I-期数', 'B-债券种类', 'I-债券种类', 'I-债券种类','I-债券种类','I-债券种类']
    print(merge_elements(text, tags))
