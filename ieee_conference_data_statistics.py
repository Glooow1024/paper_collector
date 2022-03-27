# !/usr/bin/python
# -*- coding:utf-8 -*-
import ast
#import wordcloud
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
###########################################################
# 统计：根据抓取的数据统计论文keywords                    
###########################################################

fileName = 'E:\\spider\\paper_collector\\ICRA_2020.csv'

# extract all keywords
dataframe = pd.read_csv(fileName, sep=',', encoding='unicode_escape')
key_words = dataframe['key words'].dropna(axis=0, how='all').tolist()
merged_key_words = []
for data in key_words:
    merged_key_words.extend(ast.literal_eval(data))

# sort the most refered keyworks
counts = Counter(merged_key_words)
counts = sorted(counts.items(), key = lambda kv: kv[1], reverse = True)
kws = [kv[0] for kv in counts]
cnts = [kv[1] for kv in counts]

# plot vertical figure
fig=plt.figure(figsize=(12,10))
plt.bar(x=kws[0:30], height=cnts[0:30], width=0.8, ecolor='black')
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.xticks(rotation=90)
fig.autofmt_xdate()
plt.title('ICRA 2020 Statistics', fontsize=16)
plt.savefig('E:\\spider\\paper_collector\\ICRA_2020_1.png')
plt.show()

# plot horizontal figure
fig=plt.figure(figsize=(16,10))
plt.barh(y=kws[0:40], width=cnts[0:40], height=0.8)
#plt.yticks(fontsize=16)
plt.xticks(fontsize=16)
plt.title('ICRA 2020 Statistics', fontsize=16)
#plt.savefig('E:\\spider\\paper_collector\\ICRA_2020_2.png')
plt.show()
