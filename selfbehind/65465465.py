import re
import nltk
import pandas as pd
'''
with open('./engdemo.txt', encoding='utf-8') as f:
    pt = f.read()

words = [i for i in re.sub('[\s|\W]', ' ', pt).split(' ')if i != '']

dictbs={}

data = []

for word in words:
    dictbs[word.lower()] = word
    data = data + nltk.pos_tag(nltk.word_tokenize(word.lower()))
wat = [[dictbs[d[0]],d[1]]for d in data]
'''
pos = {'colorless': 'ADJ', 'ideas': 'N', 'sleep': 'V', 'furiously': 'ADV'}
pos = dict(colorless='ADJ', ideas="N", sleep="V", furiously="ADV",yuchen='N')
s='jelly royal does yuzhen'
g=nltk.word_tokenize(s)
print(nltk.pos_tag(g))

pd.DataFrame(df.feature.tolist(), columns=cols)