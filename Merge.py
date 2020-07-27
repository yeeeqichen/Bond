import json


def merge_elements(text, tags):
    def _decode_year_range():
        nonlocal blocks
        flag = 0
        for i in range(len(blocks)):
            for idx, t in enumerate(blocks[i]['tags']):
                if t == '年份' and '-' in blocks[i]['elements'][idx]:
                    flag = 1
                    span = blocks[i]['elements'][idx]
                    j = span.find('-')
                    begin = span[:j]
                    end = span[j + 1:j + len(begin) + 1]
                    tail = span[j + len(begin) + 1:]
                    blocks[i]['elements'][idx] = begin + tail
                    for y in range(int(begin) + 1, int(end) + 1):
                        temp = dict()
                        temp['elements'] = []
                        for e in blocks[i]['elements']:
                            temp['elements'].append(e)
                        temp['tags'] = blocks[i]['tags']
                        temp['elements'][idx] = str(y) + tail
                        blocks.append(temp)
        return flag == 1

    def _decode_num_range():
        pass
    idx = 0
    blocks = []
    block = dict()
    block['elements'] = []
    block['tags'] = []
    while idx < len(tags):
        if 'B' in tags[idx]:
            # 如果要素不是修饰词并且要素已经在当前block中出现，我们认为这是一支新的债券（要素并列的情况后处理）
            if tags[idx][2:] != '修饰语' and tags[idx][2:] in block['tags']:
                blocks.append(block)
                block = dict()
                block['tags'] = [tags[idx][2:]]
                ele = text[idx]
                idx += 1
                while idx < len(tags) and 'I' in tags[idx]:
                    ele += text[idx]
                    idx += 1
                block['elements'] = [ele]
            # 将此要素加入到当前要素块中
            else:
                block['tags'].append(tags[idx][2:])
                ele = text[idx]
                idx += 1
                while idx < len(tags) and 'I' in tags[idx]:
                    ele += text[idx]
                    idx += 1
                block['elements'].append(ele)
        else:
            idx += 1
    blocks.append(block)
    if _decode_year_range():
        print(blocks)

    return blocks


if __name__ == '__main__':
    path = '/Users/maac/Desktop/债券实体链接/hand_labeled.json'
    with open(path) as f:
        for line in f:
            dic = json.loads(line)
            blocks = merge_elements(dic['text'], dic['tags'])

