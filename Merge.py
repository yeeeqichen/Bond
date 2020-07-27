import json


def merge_elements(text, tags):
    # 将形如 2015-2018年度 001-008期 展开为多只债券
    def _decode_range():
        nonlocal blocks
        flag = 0
        for idx1 in range(len(blocks)):
            for idx2, t in enumerate(blocks[idx1]['tags']):
                if (t == '年份' or t == '期数') and '-' in blocks[idx1]['elements'][idx2]:
                    flag = 1
                    span = blocks[idx1]['elements'][idx2]
                    i = 0
                    while not '0' <= span[i] <= '9':
                        i += 1
                    j = span.find('-')
                    head = span[:i]
                    begin = span[i:j]
                    length = len(begin)
                    end = span[j + 1:j + length + 1]
                    tail = span[j + length + 1:]
                    blocks[idx1]['elements'][idx2] = head + begin + tail
                    for y in range(int(begin) + 1, int(end) + 1):
                        temp = dict()
                        temp['elements'] = []
                        for e in blocks[idx1]['elements']:
                            temp['elements'].append(e)
                        temp['tags'] = blocks[idx1]['tags']
                        temp['elements'][idx2] = head + str(y).zfill(length) + tail
                        blocks.append(temp)
        return flag == 1

    print(text)
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
                if tag == '期数' and last_tag == '期数':
                    dic = dict()
                    dic['elements'] = []
                    dic['tags'] = []
                    for i in range(len(temp['tags']) - 1):
                        dic['elements'].append(temp['elements'][i])
                        dic['tags'].append(temp['tags'][i])
                    dic['elements'].append(ele)
                    dic['tags'].append(tag)
                    queue.append(dic)
                elif tag != '修饰语' and tag != '期数' and tag in temp['tags']:
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
                if tag == '期数' and last_tag == '期数':
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

            # 记录上一轮的标签情况，目前逻辑是连续出现两个期数则进入特殊模式，todo:后续可以进行补充，例如年份并列
            last_tag = tag
        else:
            idx += 1
    if special_mode:
        for b in queue:
            blocks.append(b)
    else:
        blocks.append(block)
    # 检查每支债券的元素，是否出现年份是范围或者期数是范围，如果有则对其进行展开
    _decode_range()
    print(blocks)
    return blocks


if __name__ == '__main__':
    path = '/Users/maac/Desktop/债券实体链接/hand_labeled.json'
    with open(path) as f:
        for line in f:
            dic = json.loads(line)
            blocks = merge_elements(dic['text'], dic['tags'])
    # text = '14呵呵第一期、第二期、第三期短期融资券xxx18呵呵01'
    # tags = ['B-年份', 'I-年份', 'B-发债方', 'I-发债方', 'B-期数', 'I-期数', 'I-期数', 'O', 'B-期数', 'I-期数', 'I-期数','O','B-期数', 'I-期数', 'I-期数',
    #         'B-债券类型', 'I-债券类型','I-债券类型','I-债券类型', 'I-债券类型', 'O', 'O', 'O','B-年份', 'I-年份', 'B-发债方', 'I-发债方', 'B-期数', 'I-期数']
    # merge_elements(text, tags)
