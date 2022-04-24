import jieba
import jieba.posseg as pseg
jieba.suggest_freq(('草美牛奶'), True)
w=pseg.lcut('草莓牛奶')
print(w)