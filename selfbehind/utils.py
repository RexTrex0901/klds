"""
(Demo 顯示使用 Jupyter)

1. 爬蟲抓取 香港屈臣氏資料 （已完成
2. 根據 product id 比對 excel 跟網站內容 filter 掉沒有出現在裡面的關鍵字  （1day)
3. 新增預設filter 規則（數字（中文、英文等）(0.5 day)
4. 新增一個filter 規則表，可以主動新增過濾條件 如： width 898 (0.5 day)
5. 新增 TF-IDF 功能 (3 day 含研究)
"""
import json
import re
import typing
import jieba
import httpx
import jieba.posseg as pseg
import pandas as pd
from pydantic import BaseModel
from pyquery import PyQuery as pq
import jieba.analyse

import models

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}


class Product(BaseModel):
    """Product"""
    id: str
    breadcrumbs: typing.List[str] = []
    desc: str
    name: str
    price: float

    @property
    def context(self) -> str:
        """context"""
        breadcrumbs = " ".join(self.breadcrumbs)
        return f'{self.name} {self.desc} {breadcrumbs}'.strip()

    class Config:
        """Config"""
        fields = {'id': '_id'}


def get_digit(price: str) -> typing.Optional[float]:
    """get digit"""
    try:
        ret = re.findall('\d+\.', price)[0]
        return float(ret)
    except IndexError:
        pass


def get_xlsx() -> pd.DataFrame:
    """get pandas"""
    df = pd.read_excel('./product_tag.xlsx', engine='openpyxl')
    df['Code'] = df['Code'].astype(str)
    return df


def get_product_tags_by_id(df: pd.DataFrame, product_id: str) -> pd.DataFrame:
    """filter by code"""
    return df[df['Code'] == product_id]


def get_product_by_url(url: str) -> typing.Optional[Product]:
    """get data"""
    r = httpx.get(url, headers=headers)
    if r.status_code >= 300:
        return
    print(r.status_code)
    doc = r.text
    dom = pq(doc)
    text = dom('cx-page-slot.ProductDetails').text().lstrip('產品資料\n')
    structured_data = dom('script.structured-data').text()
    breadcrumbs = [
        row['name'] for row in
        json.loads(structured_data)[0]['itemListElement']
    ]
    _id = str(r.url).split('/')[-1]
    product = {
        '_id': _id,
        'url': str(r.url),
        'name': dom('e2-product-summary > h1.ng-star-inserted').text(),
        'price': get_digit(dom('div.displayPrice').text()),
        'desc': text,
        'breadcrumbs': breadcrumbs,
    }
    return Product(**product)


def get_product_by_id(product_id: str) -> typing.Optional[Product]:
    """Get data"""
    rgx = re.compile(f'.*?{product_id}.*?', re.IGNORECASE)
    product = models.Product.find_one({'_id': rgx})
    if product:
        product = Product(**product)
    else:
        url = f'https://www.watsons.com.hk/temp/p/{product_id}'
        product = get_product_by_url(url)
        data = product.dict()
        if 'id' in data:
            data['_id'] = data['id']
            del data['id']
        models.update(models.Product, data)
        if product_id not in data['_id']:
            data['_id'] = product_id
            models.update(models.Product, data)
    return product


def show_diff_tags(
        entire_tags: typing.List[str],
        filtered_tags: typing.List[str]
):
    """print diff tags"""
    for s in (set(entire_tags) - set(filtered_tags)):
        print(s)


def show_tags_place(tags: typing.List[str], product: Product):
    """print tag in product attribute"""
    keys = product.dict().keys()
    for tag in tags:
        find = False
        for key in keys:
            value = getattr(product, key)
            if tag in str(value):
                print(f'{tag} {key}')
                find = True
        if not find:
            print(f'{tag} NOT FOUND')


def get_tags_in_context(
        tags: typing.List[str], context: str
) -> typing.List[str]:
    """

    Args:
        tags:
        context:

    Returns:
        tags list
    """
    context = context.lower()
    ret = []
    for tag in tags:
        tag = tag.lower()
        if tag in context and tag not in ret:
            ret.append(tag)
    return ret


pattern = r'([\d一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾]|\bone\b|\btwo\b|\bthree\b|\bfour\b|\bfive\b|\bsix\b|\bseven\b|\beight\b|\bnine\b|\bten\b)'


def check_by_file(text) -> bool:
    """透過filter.txt判斷"""
    with open('../filter.txt', encoding='utf-8') as f:
        pt = f.read()
    pt = "|".join(pt.strip().split())
    return re.match(pt, text) is not None


def filter_by_file(tags: typing.List[str]) -> typing.List[str]:
    """過濾掉含有filter.txt 的tag"""
    ret = [tag for tag in tags if not check_by_file(tag)]
    return ret


def check_pattern_regex(text) -> bool:
    """判斷文字是否含要過濾的字"""
    return re.match(pattern, text) is not None


def filter_pattern_regex(tags: typing.List[str]) -> typing.List[str]:
    """過濾掉客製化regex"""
    ret = [tag for tag in tags if not check_pattern_regex(tag)]
    return ret


def filter_rk(tags: typing.List[str], prodesc):
    "無詞性排序"
    c = {}
    for tag in tags:
        c[tag] = str(prodesc).count(tag)
    items = list(c.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i in range(15):
        k, n = items[i]
        print(k, n)


def filter_rk1(tags: typing.List[str], prodesc):
    "無詞性排序、合併雙歧桿菌錯別字的結果"
    c = {}
    for tag in tags:
        if tag == '雙岐桿菌':
            a = str(prodesc).count(tag)
        elif tag == '雙歧桿菌':
            b = str(prodesc).count(tag)
        else:
            c[tag] = str(prodesc).count(tag)
    c['雙岐桿菌'] = a + b
    items = list(c.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i in range(15):
        k, n = items[i]
        print(k, n)


def filter_rkwf(tags: typing.List[str], prodesc):
    "無過濾的帶詞性排序"
    c = {}
    d = {}
    for tag in tags:
        a = tag.find(' ')
        word = tag[:a]
        flag = tag[a + 1:]
        d[word] = flag
        c[word] = str(prodesc).count(word)
    items = list(c.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i in range(15):
        k, n = items[i]
        print(k, n, d[k])


def filter_rkwfdf1(tags: typing.List[str], prodesc):
    "做移x、m除詞性的帶詞性排序"
    c = {}
    d = {}
    de = ['x', 'm']
    for tag in tags:
        a = tag.find(' ')
        word = tag[:a]
        flag = tag[a + 1:]
        if flag not in de:
            d[word] = flag
            c[word] = str(prodesc).count(word)
    items = list(c.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i in range(15):
        k, n = items[i]
        print(k, n, d[k])


def filter_row(tags: typing.List[str]):
    "過濾單字、字母"
    ret = [tag for tag in tags if len(tag) > 1]
    return ret


def userdict_add(tags: typing.List[str]):
    """自定義tag詞性後加入至userdict.txt"""
    jieba.load_userdict('userdict.txt')  # 使用自定義字典
    f = open('userdict.txt', 'a', encoding='utf-8')
    noun = ['n', 'nz', 'nl', 'ng', 'vn', 'an']
    verb = ['v', 'vn']
    adj = ['a', 'an']
    for tag in tags:
        cw = 0
        cf = ''
        v = 0
        a = 0
        w = pseg.cut(tag)
        for word, flag in w:
            cw += 1
            if flag in verb:
                v = 1
            if flag in adj:
                a = 1
            if (cf == '') or (cf not in noun):
                cf = flag
            if flag in noun:
                if a == 1:
                    cf = 'an'
                if v == 1:
                    cf = 'vn'
        forwrite = ('%s %s\n') % (tag, cf)
        if (cw > 1) and (len(forwrite) > 0):
            f.writelines(forwrite)
    f.close()


def show_with_flag(tags: typing.List[str]) -> typing.List[str]:
    """顯示tag+詞性"""
    jieba.load_userdict('userdict.txt')  # 使用自定義字典
    swf = ['%s %s' % (word, flag) for tag in tags for word, flag in pseg.cut(tag)]
    return swf


def tfidf_count(q):
    """做desc的tfidf計算"""
    desc = q[q.find('desc=') + 6:q.find('price') - 2]
    keywords = jieba.analyse.extract_tags(desc, topK=15, withWeight=True, allowPOS=('n', 'nr', 'ns'))
    for item in keywords:
        print('%s(%.3f)' % (item[0], item[1]))


if __name__ == '__main__':
    product_id = '防護力'
    print(check_by_file(product_id))
