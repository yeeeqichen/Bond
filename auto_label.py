#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: auto_label.py
@time: 2020/8/11 5:16 下午
@desc:
"""
import re
from sys import argv
import json

path1 = '/data/IE/yqc/bond/names.txt'
path2 = '/data/IE/yqc/text_auto.txt'

company_tag = '-发债方'
year_tag = '-年份'
num_tag = '-期数'
kind_tag = '-修饰语'
bond_tag = '-债券类型'

company_full = '(.+有限公司|.+集团\)?公司|.+责任公司|.+股份公司|.+银行|.+商行|.+政府|.+中心|.+?市|.+省|.+社|中国铁路)'
year_full = '([0-9]{4}年?度?)'
num_full = '(\(第?[一二三四五六七八九十0-9]+期\)|第?[一二三四五六七八九十0-9]+期)'
kind_full = '([0-9]+[A-Z年]|[0-9]+个月|\(品种[一二三四五六七八九十0-9]+\)|\(.+\)' \
            '|机构|公司客户|个人|机构|绿色|短期|对公|贴现|记账式|凭证式|记账式附息|记账式贴现|' \
            '再融资|面向专业投资者公开发行|面向合格投资者公开发行|面向合格投资者非公开发行|' \
            '公开发行|非公开发行|[一二三四五六七八九十]年期|可交换|可转换)'
bond_full = '(资本债券|公司债券|超短期融资券|短期融资券|中期票据|大额存单|专项债券|项目收益债券|企业债券|集合债券|专项债券|项目收益专项公司债券' \
            '|金融债券|同业存单|国债|债务融资工具|人民币债券|央行票据|中央银行票据|资产支持票据|资产支持商业票据|一般债券)'

year_short = '([0-9]{2}|[0-9]{4})'
num_short = '([0-9]{1,3}|[一二三四五六七八九十])'
company_short = '([^0-9A-Za-z]+)'
bond_short = '(票据|附息国债|国债|大额存单|债|MTN|SCP|CD|PPN|PRN|SMECN|ABN|JX|CP)'
kind_short = '(优先|个人|机构[A-B][0-9].*|优[0-9].*|次级|贴现|贴现附息|附息|优先级|绿色|转|可转|G|C|Y|\(.*\))'

pattens_full = []
pattens_short = []
tags_full = []
tags_short = []
# -----------------------------全称部分-------------------------------------
# --------年开头-----------
# xx年xx期xx公司 修饰语 xx债券 修饰语
pattens_full.append('{}{}{}{}{}{}$'.format(year_full, num_full, company_full, kind_full, bond_full, kind_full))
tags_full.append([year_tag, num_tag, company_tag, kind_tag, bond_tag, kind_tag])
# xx年xx期xx公司xx债券xx 修饰语
pattens_full.append('{}{}{}{}{}$'.format(year_full, num_full, company_full, bond_full, kind_full))
tags_full.append([year_tag, num_tag, company_tag, bond_tag, kind_tag])

# xx年xx期xx公司 修饰语 xx债券
pattens_full.append('{}{}{}{}{}$'.format(year_full, num_full, company_full, kind_full, bond_full))
tags_full.append([year_tag, num_tag, company_tag, kind_tag, bond_tag])
# xx年xx期xx公司xx债券
pattens_full.append('{}{}{}{}$'.format(year_full, num_full, company_full, bond_full))
tags_full.append([year_tag, num_tag, company_tag, bond_tag])

# xx年xx公司 修饰语xx债券xx期xx 修饰语
pattens_full.append('{}{}{}{}{}{}$'.format(year_full, company_full, kind_full, bond_full, num_full, kind_full))
tags_full.append([year_tag, company_tag, kind_tag, bond_tag, num_tag, kind_tag])
# xx年xx公司xx债券xx期xx 修饰语
pattens_full.append('{}{}{}{}{}$'.format(year_full, company_full, bond_full, num_full, kind_full))
tags_full.append([year_tag, company_tag, bond_tag, num_tag, kind_tag])

# xx年xx公司xx期 修饰语 xx债券
pattens_full.append('{}{}{}{}{}$'.format(year_full, company_full, num_full, kind_full, bond_full))
tags_full.append([year_tag, company_tag, num_tag, kind_tag, bond_tag])
# xx年xx公司xx期xx债券
pattens_full.append('{}{}{}{}$'.format(year_full, company_full, num_full, bond_full))
tags_full.append([year_tag, company_tag, num_tag, bond_tag])

# xx年xx公司 修饰语 xx债券 xx期
pattens_full.append('{}{}{}{}{}$'.format(year_full, company_full, kind_full, bond_full, num_full))
tags_full.append([year_tag, company_tag, kind_tag, bond_tag, num_tag])
# xx年xx公司xx债券xx期
pattens_full.append('{}{}{}{}$'.format(year_full, company_full, bond_full, num_full))
tags_full.append([year_tag, company_tag, bond_tag, num_tag])

# xx年xx公司 修饰语 xx债券
pattens_full.append('{}{}{}$'.format(year_full, company_full, kind_full, bond_full))
tags_full.append([year_tag, company_tag, kind_tag, bond_tag])
# xx年xx公司xx债券
pattens_full.append('{}{}{}$'.format(year_full, company_full, bond_full))
tags_full.append([year_tag, company_tag, bond_tag])

# xx年 修饰语 xx期 xx债券 修饰语
pattens_full.append('{}{}{}{}$'.format(year_full, kind_full, num_full, bond_full, kind_full))
tags_full.append([year_tag, kind_tag, num_tag, bond_tag, kind_tag])
# xx年 修饰语 xx期 xx债券
pattens_full.append('{}{}{}{}$'.format(year_full, kind_full, num_full, bond_full))
tags_full.append([year_tag, kind_tag, num_tag, bond_tag])

# --------公司开头----------
# xx有限公司xx年xx期xx债券xx(品种)
pattens_full.append('{}{}{}{}{}$'.format(company_full, year_full, num_full, bond_full, kind_full))
tags_full.append([company_tag, year_tag, num_tag, bond_tag, kind_tag])

# xx公司xx年xx期 修饰 xx债
pattens_full.append('{}{}{}{}{}$'.format(company_full, year_full, num_full, kind_full, bond_full))
tags_full.append([company_tag, year_tag, num_tag, kind_tag, bond_tag])
# xx公司xx年xx期xx债
pattens_full.append('{}{}{}{}$'.format(company_full, year_full, num_full, bond_full))
tags_full.append([company_tag, year_tag, num_tag, bond_tag])

# xx有限公司xx年 修饰语 xx债券xx期xx品种
pattens_full.append('{}{}{}{}{}{}$'.format(company_full, year_full, kind_full, bond_full, num_full, kind_full))
tags_full.append([company_tag, year_tag, kind_tag, bond_tag, num_tag, kind_tag])
# xx有限公司xx年xx债券xx期xx品种
pattens_full.append('{}{}{}{}{}$'.format(company_full, year_full, bond_full, num_full, kind_full))
tags_full.append([company_tag, year_tag, bond_tag, num_tag, kind_tag])

# xx公司xx年 修饰语 xx债xx期
pattens_full.append('{}{}{}{}{}$'.format(company_full, year_full, kind_full, bond_full, num_full))
tags_full.append([company_tag, year_tag, kind_tag, bond_tag, num_tag])
# xx公司xx年xx债xx期
pattens_full.append('{}{}{}{}$'.format(company_full, year_full, bond_full, num_full))
tags_full.append([company_tag, year_tag, bond_tag, num_tag])

# xx公司xx年 修饰语 xx债券
pattens_full.append('{}{}{}{}$'.format(company_full, year_full, kind_full, bond_full))
tags_full.append([company_tag, year_tag, kind_tag, bond_tag])
# xx公司xx年xx债券
pattens_full.append('{}{}{}$'.format(company_full, year_full, bond_full))
tags_full.append([company_tag, year_tag, bond_tag])

# xxx公司xx期 修饰语 xx债券
pattens_full.append('{}{}{}{}$'.format(company_full, num_full, kind_full, bond_full))
tags_full.append([company_tag, num_tag, kind_tag, bond_tag])
# xxx公司xx期xx债券
pattens_full.append('{}{}{}$'.format(company_full, num_full, bond_full))
tags_full.append([company_tag, num_tag, bond_tag])

# xx公司 修饰语 xx债券xx年xx期
pattens_full.append('{}{}{}{}{}$'.format(company_full, kind_full, bond_full, year_full, num_full))
tags_full.append([company_tag, kind_tag, bond_tag, year_tag, num_tag])
# xx公司xx债券xx年xx期
pattens_full.append('{}{}{}{}$'.format(company_full, bond_full, year_full, num_full))
tags_full.append([company_tag, bond_tag, year_tag, num_tag])

# xx公司 修饰语 xx 年 xx债券 xx期
pattens_full.append('{}{}{}{}{}$'.format(company_full, kind_full, year_full, bond_full, num_full))
tags_full.append([company_tag, kind_tag, year_tag, bond_tag, num_tag])
# xx公司 修饰语 xx 年 xx债券 xx期 xx 品种
pattens_full.append('{}{}{}{}{}{}$'.format(company_full, kind_full, year_full, bond_full, num_full, kind_full))
tags_full.append([company_tag, kind_tag, year_tag, bond_tag, num_tag, kind_tag])
# xx公司 修饰语 xx 年 xx债券 修饰语 xx期 xx 品种
pattens_full.append('{}{}{}{}{}{}{}$'.format(company_full, kind_full, year_full, bond_full, kind_full, num_full, kind_full))
tags_full.append([company_tag, kind_tag, year_tag, bond_tag, kind_tag, num_tag, kind_tag])


# -------------------------缩写部分-------------------------------------
# -------------------债券开头----------------
pattens_short.append('{}{}{}{}$'.format(bond_short, year_short, num_short, kind_short))
tags_short.append([bond_tag, year_tag, num_tag, kind_tag])
pattens_short.append('{}{}{}$'.format(bond_short, year_short, num_short))
tags_short.append([bond_tag, year_tag, num_tag])

# -------------------年份开头----------------
pattens_short.append('{}{}{}{}$'.format(year_short, kind_short, bond_short, num_short))
tags_short.append([year_tag, kind_tag, bond_tag, num_tag])
pattens_short.append('{}{}{}$'.format(year_short, company_short, kind_short))
tags_short.append([year_tag, company_tag, kind_tag])
pattens_short.append('{}{}{}{}$'.format(year_short, company_short, kind_short, num_short))
tags_short.append([year_tag, company_tag, kind_tag, num_tag])

pattens_short.append('{}{}{}{}$'.format(year_short, company_short, bond_short, num_short))
tags_short.append([year_tag, company_tag, bond_tag, num_tag])

pattens_short.append('{}{}{}{}{}$'.format(year_short, company_short, bond_short, num_short, kind_short))
tags_short.append([year_tag, company_tag, bond_tag, num_tag, kind_tag])
pattens_short.append('{}{}{}{}$'.format(year_short, company_short, num_short, kind_short))
tags_short.append([year_tag, company_tag, num_tag, kind_tag])

pattens_short.append('{}{}{}$'.format(year_short, company_short, num_short))
tags_short.append([year_tag, company_tag, num_tag])

pattens_short.append('{}{}{}{}{}$'.format(year_short, company_short, kind_short, bond_short, kind_short))
tags_short.append([year_tag, company_tag, kind_tag, bond_tag, kind_tag])
pattens_short.append('{}{}{}{}$'.format(year_short, company_short, bond_short, kind_short))
tags_short.append([year_tag, company_tag, bond_tag, kind_tag])

pattens_short.append('{}{}{}$'.format(year_short, company_short, bond_short))
tags_short.append([year_tag, company_tag, bond_tag])

# ----------------字母开头----------------

pattens_short.append('{}{}{}{}$'.format(kind_short, company_short, num_short, kind_short))
tags_short.append([kind_tag, company_tag, num_tag, kind_tag])
pattens_short.append('{}{}{}$'.format(kind_short, company_short, num_short))
tags_short.append([kind_tag, company_tag, num_tag])
pattens_short.append('{}{}{}$'.format(kind_short, company_short, kind_short))
tags_short.append([kind_tag, company_tag, kind_tag])

pattens_short.append('{}{}{}{}$'.format(kind_short, year_short, company_short, num_short))
tags_short.append([kind_tag, year_tag, company_tag, num_tag])
pattens_short.append('{}{}{}{}$'.format(kind_short, year_short, company_short, kind_short))
tags_short.append([kind_tag, year_tag, company_tag, kind_tag])
pattens_short.append('{}{}{}{}{}$'.format(kind_short, year_short, company_short, num_short, kind_short))
tags_short.append([kind_tag, year_tag, company_tag, num_tag, kind_tag])

# ---------------公司开头----------------

pattens_short.append('{}{}{}{}{}$'.format(company_short, kind_short, bond_short, year_short, num_short))
tags_short.append([company_tag, kind_tag, bond_tag, year_tag, num_tag])
pattens_short.append('{}{}{}{}{}$'.format(company_short, bond_short, year_short, num_short, kind_short))
tags_short.append([company_tag, bond_tag, year_tag, num_tag, kind_tag])
pattens_short.append('{}{}{}{}$'.format(company_short, bond_short, year_short, num_short))
tags_short.append([company_tag, bond_tag, year_tag, num_tag])
pattens_short.append('{}{}{}$'.format(company_short, year_short, num_short))
tags_short.append([company_tag, year_tag, num_tag])

full_names = []
short_names = []

with open(path1) as f:
    for line in f:
        full, short = line.strip('\n').split(' ')
        full_names.append(full)
        short_names.append(short)

with open(path2) as f:
    for line in f:
        dic = dict()
        flag = 0
        seq = ['O'] * len(line)
        for full, short in zip(full_names, short_names):
            idx2 = line.find(short)
            if idx2 != -1:
                for patten, tag in zip(pattens_short, tags_short):
                    gr = re.match(patten, short)
                    if gr:
                        flag = 1
                        for group, t in zip(gr.groups(), tag):
                            seq[idx2] = 'B' + t
                            for i in range(1, len(group)):
                                seq[idx2 + i] = 'I' + t
                            idx2 += len(group)
                        break
            idx1 = line.find(full)
            if idx1 != -1:
                for patten, tag in zip(pattens_full, tags_full):
                    gr = re.match(patten, full)
                    if gr:
                        flag = 1
                        for group, t in zip(gr.groups(), tag):
                            seq[idx1] = 'B' + t
                            for i in range(1, len(group)):
                                seq[idx1 + i] = 'I' + t
                            idx1 += len(group)
                        break
        if flag == 1:
            dic['tags'] = seq
            dic['text'] = line
            print(json.dumps(dic, ensure_ascii=False))
