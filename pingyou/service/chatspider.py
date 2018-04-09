import requests
import lxml.html
import time
import re
import mongoengine

from pymongo import MongoClient
from fake_useragent import UserAgent
from pingyou.models import WeChat

mongoengine.connect('pingyou', host='localhost', port=27017)
client = MongoClient('localhost', 27017)
db = client.pingyou
wechat = db.wechat


etree = lxml.html.etree
ua = UserAgent()
headers = {
    'user-agent': ua.random
}

query_url = 'http://weixin.sogou.com/weixin?&query=%E6%96%B0%E7%A7%91%E6%95%99%E5%8A%A1'
session = requests.Session()
query_html = session.get(query_url, headers=headers)
time.sleep(2)

query_html = etree.HTML(query_html.content.decode())
url = query_html.xpath("//p[@class='tit'][1]/a/@href")[0]
print(url)


new_html = session.get(url, headers=headers).content.decode()


pattern = re.compile('var msgList = (.*)?;')
dic = re.search(pattern,new_html)

data = dic.groups()[0]
data = eval(data)


jiaowu_wechat = []

for i in range(0,len(data['list']),2):
    new = {}
    new_wechat = None
    new['title'] = data['list'][i]['app_msg_ext_info']['title']
    new['img'] = data['list'][i]['app_msg_ext_info']['cover']
    new['content_url'] = "location.href='" + url + "'"
    new['intro'] = data['list'][i]['app_msg_ext_info']['digest']
    new['date'] = data['list'][i+1]['comm_msg_info']['datetime']
    new_wechat = WeChat.objects(title=new['title'], date= new['date']).first()
    if new_wechat:
        new_wechat.update(new)
    else:
        jiaowu_wechat.append(new)
    if data['list'][i]['app_msg_ext_info']['multi_app_msg_item_list']:
        for item in data['list'][i]['app_msg_ext_info']['multi_app_msg_item_list']:
            new = {}
            new_wechat = None
            new['title'] = item['title']
            new['img'] = item['cover']
            new['content_url'] = "location.href='" + url + "'"
            new['intro'] = item['digest']
            new['date'] = data['list'][i + 1]['comm_msg_info']['datetime']
            new_wechat = WeChat.objects(title=new['title'], date=new['date']).first()
            if new_wechat:
                new_wechat.update(new)
            else:
                jiaowu_wechat.append(new)
if jiaowu_wechat:
    result = wechat.insert_many(jiaowu_wechat)
