import re
from sys import argv
import json

path1 = '/data/IE/yqc/bond/names.txt'
path2 = '/data/IE/yqc/text_auto.txt'

company_full = '(.+有限公司|.+集团\)?公司|.+责任公司|.+银行|.+商行|.+政府|.+中心|.+?市|.+省|.+社)'
year_full = '([0-9]{4}年?度?)'
num_full = '(\(第?[一二三四五六七八九十0-9]+期\)|第?[一二三四五六七八九十0-9]+期)'
kind_full = '(\(品种[一二三四五六七八九十0-9]+\)|\(.+\))'
bond_full = '(.*票据|.*债券|.*证券|.*融资券|.*收据|.*工具|.*存单|.+附息|.+贴现|公开发行.*?债券)'

company_tag = '-公司'
year_tag = '-年份'
num_tag = '-期数'
kind_tag = '-种类'
bond_tag = '-债券名'
pattens = []
tags = []
# xx年xx公司xx债券xx期xx品种
pattens.append('{}{}{}{}{}'.format(year, company, bond, num, kind))
tags.append([year_tag, company_tag, bond_tag, num_tag, kind_tag])
# xx年xx公司xx债券xx期
pattens.append('{}{}{}{}'.format(year, company, num, bond))
tags.append([year_tag, company_tag, num_tag, bond_tag])
# xx年xx公司xx债券xx期
pattens.append('{}{}{}{}'.format(year, company, bond, num))
tags.append([year_tag, company_tag, bond_tag, num_tag])
# xx年xx公司xx债券
pattens.append('{}{}{}'.format(year, company, bond))
tags.append([year_tag, company_tag, bond_tag])
# xx有限公司xx年xx期xx债券xx(品种)
pattens.append('{}{}{}{}{}'.format(company, year, num, bond, kind))
tags.append([company_tag, year_tag, num_tag, bond_tag, kind_tag])
# xx公司xx年xx期xx债
pattens.append('{}{}{}{}'.format(company, year, num, bond))
tags.append([company_tag, year_tag, num_tag, bond_tag])
# xx有限公司xx年xx债券xx期xx品种
pattens.append('{}{}{}{}{}'.format(company, year, bond, num, kind))
tags.append([company_tag, year_tag, bond_tag, num_tag, kind_tag])
# xx公司xx年xx债xx期
pattens.append('{}{}{}{}'.format(company, year, bond, num))
tags.append([company_tag, year_tag, bond_tag, num_tag])
# xx公司xx年xx债券
pattens.append('{}{}{}'.format(company, year, bond))
tags.append([company_tag, year_tag, bond_tag])
# xxx公司xx期xx债券
pattens.append('{}{}{}'.format(company, num, bond))
tags.append([company_tag, num_tag, bond_tag])
# xx公司xx债券xx年xx期
pattens.append('{}{}{}{}'.format(company, bond, year, num))
tags.append([company_tag, bond_tag, year_tag, num_tag])



#xx公司公开发行xxx债券的情况：
pattens.append('{}(公开发行|非公开发行|面向合格投资者公开发行|面向合格投资者非公开发行){}{}{}'.format(company, year, bond, num))
tags.append([company_tag, bond_tag, year_tag, bond_tag, num_tag])
pattens.append('{}(公开发行|非公开发行|面向合格投资者公开发行|面向合格投资者非公开发行){}{}{}'.format(company, year, num, bond))
tags.append([company_tag, bond_tag, year_tag, num_tag, bond_tag])
# 这里处理不规则的公司名:依赖于中间的年份或期数进行划分

# xx公司xx年xx期xx债
pattens.append('(.+?){}{}{}'.format(year, num, bond))
tags.append([company_tag, year_tag, num_tag, bond_tag])
# xx公司xx期xx债，这里处理不规则的公司名
pattens.append('(.+?){}{}'.format(num, bond))
tags.append([company_tag, num_tag, bond_tag])

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
        for full in full_names:
            idx = line.find(full)
            if idx != -1:
                seq = ['O'] * len(line)
                for patten, tag in zip(pattens, tags):
                    gr = re.match(patten, full)
                    if gr:
                        # print(gr.groups())
                        for group, t in zip(gr.groups(), tag):
                            seq[idx] = 'B' + t
                            for i in range(1, len(group)):
                                seq[idx + i] = 'I' + t
                            idx += len(group)
                        dic = dict()
                        dic['tags'] = seq
                        dic['text'] = line
                        print(json.dumps(dic, ensure_ascii=False))
                        break
                break

