"""
@description：
    对外提供add_elements_to_blocks 方法，用于处理要素缺失的情况，从正文中补充要素
@author: yeeeqichen
"""


def add_elements_to_blocks(text, article, blocks):
    """
    :param text: mention所在的text（标题），例如公告
    :param article: 正文
    :param blocks: 组合要素得到的债券
    :return: 补充完要素后的债券
    """

    def _extract_articles(article):
        nonlocal company
        nonlocal year
        nonlocal num

    # 从正文中解析出三种要素（可能有多个)
    company = []
    year = []
    num = []
    _extract_articles(article)
    
    for i in range(len(blocks)):
        if '发债方' not in blocks[i]['tags']:
            # 补充发债方
            pass
        if '年份' not in blocks[i]['tags']:
            # 补充年份
            pass
        if '期数' not in blocks[i]['tags']:
            # 补充期数
            pass
        if '修饰语' not in blocks[i]['tags']:
            # 补充修饰语，这里主要是品种
            pass

    pass
