# coding=utf-8
import os
from os.path import join

## 路径相关配置，无需修改
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CORPUS_DIR = join(ROOT_DIR, 'corpus')

## 算法相关参数，可能需要根据具体的目标语料进行调整（一般选用默认参数即可）

# D-Topwords 算法相关参数
LEN_C = 50                # 越大的越倾向于取得越短的词（在使用中，若发现词长过长例如“数据结构教程”，则可以考虑减小该值）
VARPHI = 0.9              # D-Topwords 中领域词典和通用词典的比重（一般不需要调整该值）
DTOP_THRESHOLD = 0.0004   # 过滤阈值，D-Topwords 值小于该值的词直接过滤不会出现在最后词表

# Pattern Filter 算法相关参数，其中包含了 wikipedia 抽取出的词和 lily 算法中的正模板（负模板由于效果太差没有使用）
PATTERN_THRESHOLD = 2     # 具体算法参见 pipeline.py 72行，越大的值越严格

# ABC 规则过滤，无相关参数需要调节

USE_RULE0 = False
