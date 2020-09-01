# 债券名实体链接系统
模型关键要素：
* 债券要素NER 
* 债券要素组合规则 
* Universal Sentence Encoder 获取债券名的向量表示 
* 使用PCA对债券名向量进行降维
* 依据债券类型将债券名库划分为小的子集，并在每个子集中建立KD-Tree 
* 在KD-Tree中寻找k近邻，然后对结果进行重排得到最终链接结果

模型流程图:
![流程图](https://raw.githubusercontent.com/yeeeqichen/pictures/master/1597044790595.jpg)


模型运行：
* 在EntityLinker.py文件中定义了link()方法，该方法接收输入(input)形如：
 ```[{“bond_arg”: [], “paragraph”: “”, “pos”: …, “text”: “”, “type”: …}, …]```
* 该方法返回标题和正文的链接结果(title_result, article_result)以及标题和正文的文本(title, article)：
``` [{“mention”: .., “entity”: ..}, ..]```

配置文件参数说明： 
* embed_file_full:存放债券全称的USE编码向量文件
* embed_file_short:存放债券简称的USE编码向量文件
* name_file:债券名库文件
* full_to_id:债券名库索引文件
* map_table:全称简称映射表文件 
* USE:USE模型地址

* knn:近邻的数量
* thresh_hold:判断是否在债券名库中的阈值
* pca_dim:PCA降维后的维数

* use_USE:是否使用USE模型编码向量
* use_PAC:是否使用PCA进行降维
* is_news:是否是新闻语料
* use_LSH:是否使用LSH
