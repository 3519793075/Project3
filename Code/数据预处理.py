# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 15:54:08 2022

@author: 86157
"""
import pandas as pd 
import re
import jieba.posseg as psg
import numpy as np

#一.评论预处理
#1.评论去重
reviews = pd.read_csv("数据/reviews.csv")
reviews = reviews[['content','content_type']].drop_duplicates()
content = reviews['content']

#2.数据清洗

strinfo = re.compile('[0-9a-zA-Z]|京东|美的|电热水器|热水器|')
content = content.apply(lambda x: strinfo.sub('', x))

#二.评论分词
#分词，词性标注，去除停用词代码
#分词
worker = lambda s: [(x.word,x.flag) for x in psg.cut(s)] #自定义简单分词函数
seg_word = content.apply(worker)

#将词语转为数据框形式，一列是词，一列是词语所在的句子id，最后一列是词语在该句子中的位置
n_word = seg_word.apply(lambda x:len(x)) #每一评论中词的个数
n_content = [[x+1]*y for x,y in zip(list(seg_word.index),list(n_word))]
index_content = sum(n_content,[]) #将嵌套的列表展开，作为词所在评论的id

seg_word = sum(seg_word,[])
word = [x[0] for x in seg_word] #词
nature = [x[1] for x in seg_word] #词性

content_type = [[x]*y for x,y in zip(list(reviews['content_type']),
                                     list(n_word))]
content_type = sum(content_type,[]) #评论类型

result = pd.DataFrame({"index_content":index_content,
                       "word":word,
                       "nature":nature,
                       "content_type":content_type})
#删除标点符号
result = result[result['nature'] != 'x'] #x为标点符号

#删除停用词
stop_path = open("数据/stoplist.txt",'r',encoding='utf-8')
stop = stop_path.readlines()
stop = [x.replace('\n','') for x in stop]
word = list(set(word)-set(stop))
result = result[result['word'].isin(word)]

#构造各词在对应评论的位置列
n_word = list(result.groupby(by = ['index_content'])['index_content'].count())
index_word = [list(np.arange(0,y)) for y in n_word]
index_word = sum(index_word,[]) #表示词语在该评论中的位置

#合并评论id，评论中词的id，词，词性，评论类型
result['index_word'] = index_word

#提取含有名词的评论

# 提取含有名词类的评论
ind = result[['n' in x for x in result['nature']]]['index_content'].unique()
result = result[[x in ind for x in result['index_content']]]



#绘制词云

import matplotlib.pyplot as plt
from wordcloud import WordCloud

frequencies = result.groupby(by = ['word'])['word'].count()
frequencies = frequencies.sort_values(ascending = False)
backgroud_Image=plt.imread('数据/pl.jpg')
wordcloud = WordCloud(font_path="simhei.ttf",
                      max_words=100,
                      background_color='white',
                      mask=backgroud_Image)
my_wordcloud = wordcloud.fit_words(frequencies)
plt.imshow(my_wordcloud)
plt.axis('off') 
plt.show()

# 将结果写出
result.to_csv("数据/word.csv", index = False, encoding = 'utf-8')


                                    













