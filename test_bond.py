# coding=UTF-8
import re
# company_full = '(.+有限公司|.+集团\)?公司|.+责任公司|.+银行|.+商行|.+政府|.+中心|.+?市|.+省|.+社|中国铁路)'
# year_full = '([0-9]{4}年?度?)'
# num_full = '(\(第?[一二三四五六七八九十0-9]+期\)|第?[一二三四五六七八九十0-9]+期)'
# kind_full = '([0-9][A-Z]|\(品种[一二三四五六七八九十0-9]+\)|\(.+\)|个人|对公|贴现|记账式|凭证式|记账式附息|记账式贴现|再融资|面向专业投资者公开发行|面向合格投资者公开发行|面向合格投资者非公开发行|公开发行|非公开发行|[一二三四五六七八九十]年期)'
# bond_full = '(可交换公司债券|可转换公司债券|可续期公司债券|超短期融资券|短期融资券|中期票据|大额存单|公司债券|置换专项债券|项目收益债券|企业债券|项目专项债券|项目收益专项公司债券|金融债券|专项债券|同业存单|国债|定向债务融资工具)'
#
# pattens_full = []
# name = '2002年记帐式(六期)国债'
# # xx年 修饰语 xx期 xx债券
# pattens_full.append('2002年记账式{}国债'.format(num_full))
# gr = re.match('{}{}{}{}{}{}'.format(company_full, kind_full, year_full, bond_full, num_full, kind_full), '青州市宏利水务有限公司非公开发行2020年公司债券(第一期)(保障性住房)')
# if gr:
#     print(gr.groups())

full_names = []
path1 = '/Users/maac/Desktop/债券实体链接/names.txt'
# 金融债券类
financial = ['人民币债券', '短期融资券', '超短期融资券', '债务融资工具', '中期票据', '大额存单', '集合票据',
             '项目收益票据', '资产支持商业票据', '资产支持票据', '同业存单', '金融债券', '定期债务', '资本补充债券',
             '资产支持受益凭证', '融资券']
# 政府债券类
govern = ['一般债券', '专项债券', '国债', '建设债券', '央行票据', '中央银行票据', '政府债券', '置换债券']
# 公司债券类
company = ['公司债券', '二级资本债券', '企业债券', '资本债券', '项目收益债券', '私募债券', '私募债', '集合债券']
# 证券类
stock = ['证券', '资产支持专项计划']

bonds = financial + govern + company + stock

cnt = 0
with open(path1) as f:
    for line in f:
        flag = 0
        full, short = line.strip('\n').split(' ')
        for bond in bonds:
            if bond in full:
                flag = 1
                break
        if flag == 0:
            cnt += 1
            print(full)
print(cnt)
# print(len(bonds))
