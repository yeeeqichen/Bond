import json
path = '/Users/maac/Desktop/badcase.txt'
data = []
with open(path) as f:
    for line in f:
        dic = dict()
        dic['content'] = line
        data.append(dic)
with open('samples.json', 'w') as f:
    f.write(json.dumps(data, ensure_ascii=False))


