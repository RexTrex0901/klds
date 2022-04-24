import jieba
import jieba.posseg as pseg

jieba.load_userdict('userdict.txt')

tags=['快跑']

def userdict_add(tags):
    """自定義tag詞性後加入至userdict.txt"""
    jieba.load_userdict('userdict.txt')#使用自定義字典
    f = open('userdict.txt', 'a', encoding='utf-8')
    noun = ['n', 'nz', 'nl', 'ng', 'vn', 'an']
    verb=['v','vn']
    adj=['a','an']
    for tag in tags:
        cw = 0
        cf=''
        v=0
        a=0
        w = pseg.cut(tag)
        for word, flag in w:
            cw += 1
            if flag in verb:
                v=1
            if flag in adj:
                a=1
            if (cf == '') or (cf not in noun):
                cf = flag
            if flag in noun :
                if a==1:
                    cf = 'an'
                if v==1:
                    cf = 'vn'
        forwrite = ('%s %s\n') % (tag, cf)
        if (cw > 1) and (len(forwrite) > 0):
            f.writelines(forwrite)
            print(forwrite)
    f.close()
    print('已將%d詞彙寫入dict'%(len(tags)))

s=['芒果萃取物',
 '香蕉萃取物',
 '香橙萃取物',
 '百香果萃取物',
 '番石榴萃取物',
 '萃取物',
 '乳桿菌',
 '乾酪乳桿菌',
 '副乾酪乳桿菌',
 '瑞士乳桿菌',
 '植物乳桿菌',
 '唾液乳桿菌',
 '嗜酸乳桿菌',
 '雙歧桿菌',
 '雙岐桿菌',
 '兒童',
 '奶油粉',
 '乳化劑',
 '水果混合萃取物粉',
 '乳酸菌混合粉',]
userdict_add(s)