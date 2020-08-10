# 债券名实体链接系统
模型关键要素：
* 债券要素NER 
* 债券要素组合规则 
* Universal Sentence Encoder 获取债券名的向量表示 
* 通过余弦相似度获得TOP K候选 
* 在候选中进行消岐获得最终链接结果(目前按照相似度最高给出预测) 

模型流程图:
![流程图](https://raw.githubusercontent.com/yeeeqichen/pictures/master/1597044790595.jpg)
