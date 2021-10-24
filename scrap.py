import requests
from lxml import etree
import re

def getPage(formulaUrl:str)->int:
    res=requests.get(formulaUrl)
    html=etree.HTML(res.text)
    href=html.xpath('//a[@class="last pagination-item "]/@href')[0]
    n=re.search('(?<=pn=)\d+',href).group()
    return int(n)

def getThreadList(pageUrl:str)->dict:
    ref='https://tieba.baidu.com'
    res=requests.get(pageUrl)
    html=etree.HTML(res.text)
    title=html.xpath('//a[@class="j_th_tit "]/@title')
    url=html.xpath('//a[@class="j_th_tit "]/@href')
    d=dict(zip(title,url))
    return d

def getPosts(postUrl:str)->dict:
    pass

if __name__=='__main__':
    url=input('url of forum')
    threadUrlList={}
    nPage=getPage()
    postDict={}
    for n in range(1,nPage+1):
        nUrl=url+'?pn='+n
        threadUrlList|=getThreadUrls()

    for threadUrl in threadUrlList:
        postDict+=getPosts()



