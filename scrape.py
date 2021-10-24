import requests
from lxml import etree
import re
import logging

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

def start(forumUrl):
    logging.info(f'Start scraping {formulaUrl}')
    threadUrlList={}
    nPage=getPage()
    postDict={}
    for n in range(1,nPage+1):
        nUrl=url+'?pn='+n
        threadUrlList|=getThreadUrls()

    for threadUrl in threadUrlList:
        postDict+=getPosts()

if __name__=='__main__':
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(funcName)s : %(message)s',
            datefmt'%Y/%m/%d %H:%M:%S'
            )
    url=input('url of forum')
    start(url)


