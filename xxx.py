import re
from sys import argv
import json

path1 = '/data/IE/yqc/bond/names.txt'
path2 = 'auto_full.txt'


year = '([0-9]{2}|[0-9]{4})'
num = '([0-9]{1,3}|[一二三四五六七八九十])'
company = '([^0-9A-Za-z]+)'
bond = '(票据|附息国债|国债|可转债|转债|可续期债|绿色债|债|MTN|SCP|CD|PPN|PRN|SMECN|ABN|JX|CP|S|G|Y|P|C)'
kind = '(优先[A-C][0-9]?|[A-C][0-9]?|次[0-9]?|优[0-9]?|次级|优先级)'

bond_tag = '-债券名'
company_tag = '-公司'
year_tag = '-年份'
num_tag = '-期数'
kind_tag = '-种类'
pattens = []
tags = []
# 年份开头
pattens.append('{}{}{}{}'.format(year, company, bond, num))
tags.append([year_tag, company_tag, bond_tag, num_tag])

pattens.append('{}{}{}{}{}'.format(year, company, bond, num, kind))
tags.append([year_tag, company_tag, bond_tag, num_tag, kind_tag])
pattens.append('{}{}{}{}'.format(year, company, num, kind))
tags.append([year_tag, company_tag, num_tag, kind_tag])

pattens.append('{}{}{}{}'.format(year, company, bond, num))
tags.append([year_tag, company_tag, bond_tag, num_tag])
pattens.append('{}{}{}'.format(year, company, num))
tags.append([year_tag, company_tag, num_tag])

pattens.append('{}{}{}{}'.format(year, company, bond, kind))
tags.append([year_tag, company_tag, bond_tag, kind_tag])
pattens.append('{}{}{}'.format(year, company, kind))
tags.append([year_tag, company_tag, kind_tag])

pattens.append('{}{}{}{}'.format(year, company, bond, kind))
tags.append([year_tag, company_tag, kind_tag])
pattens.append('{}{}{}'.format(year, company, kind))
tags.append([year_tag, company_tag, bond_tag, kind_tag])

pattens.append('{}{}{}'.format(year, company, bond))
tags.append([year_tag, company_tag, bond_tag])
pattens.append('{}{}'.format(year, company))
tags.append([year_tag, company_tag])

# 字母开头
pattens.append('{}{}{}{}'.format(bond, company, num, kind))
tags.append([bond_tag, company_tag, num_tag, kind_tag])

pattens.append('{}{}{}{}'.format(bond, year, company, num))
tags.append([bond_tag, year_tag, company_tag, num_tag])

# 公司开头
pattens.append('{}{}{}{}{}'.format(company, bond, year, num, kind))
tags.append([company_tag, bond_tag, year_tag, num_tag, kind_tag])
pattens.append('{}{}{}{}'.format(company, bond, year, num))
tags.append([company_tag, bond_tag, year_tag, num_tag])
pattens.append('{}{}{}'.format(company, year, num))
tags.append([company_tag, year_tag, num_tag])

full_names = []
short_names = []
labeled_text = []

with open(path1) as f:
    for line in f:
        full, short = line.strip('\n').split(' ')
        full_names.append(full)
        short_names.append(short)


with open(path2) as f:
    for line in f:
        dic = json.loads(line)
        text = dic['text']
        seq = dic['tags']
        for short in short_names:
            idx = text.find(short)
            if idx != -1:
                for patten, tag in zip(pattens, tags):
                    gr = re.match(patten, short)
                    if gr:
                        # print(line)
                        for group, t in zip(gr.groups(), tag):
                            seq[idx] = 'B' + t
                            for i in range(1, len(group)):
                                seq[idx + i] = 'I' + t
                            idx += len(group)
                        dic['tags'] = seq
                        break
        print(json.dumps(dic, ensure_ascii=False))

