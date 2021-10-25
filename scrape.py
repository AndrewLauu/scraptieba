import requests
from lxml import etree
import re
import logging

def getForumInfo(forumUrl:str)->tuple:
    """
    获取贴吧页码数
    """
    res=requests.get(forumUrl)
    html=etree.HTML(res.text)
    nThread,nPost,nMember=html.xpath('//div[@class="th_footer_l"]/span[@class="red_text"][position()<=3]/text()')
    nThread=int(nThread)
    nPost=int(nPost)
    nMember=int(nMember)
    nPage=1+nThread//50
    #n=re.search('(?<=pn=)\d+',href).group()
    return nPage,nThread,nPost,nMember

def getThreadInfo(pageUrl:str)->dict:
    ref='https://tieba.baidu.com'
    res=requests.get(pageUrl)
    html=etree.HTML(res.text)
    title=html.xpath('//a[@class="j_th_tit "]/@title')
    url=html.xpath('//a[@class="j_th_tit "]/@href')
    #d=
    # {
    #  url:,
    #  title:
    # },
    d={
        "thread_title":title,
        "thread_href":url
    }
    return d

def getPosts(postUrl:str)->dict:


    pass

def start(forumUrl):
    logging.info(f'Start scraping {forumUrl}')
    nPage,nThread,nPost,nMember=getForumInfo()
    #threadsPool=
    #[
    # {
    #  url:,
    #  title:
    # },
    # {
    #  url:,
    #  title:
    # },
    # ...
    #]
    threadsPool={}
    for n in range(nPage):
        forumPageUrl=f'{forumUrl}&pn={50*n}'
        threadsPool.append(getThreadInfo(forumPageUrl))

    postDict={}
    for threadInfo in threadsPool:
        threadUrl=threadInfo["thread_href"]
        threadTitle=threadInfo["thread_title"]
        
        postDict+=getPosts(threadUrl)


if __name__=='__main__':
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(funcName)s : %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S'
            )
    url=input('url of forum')
    url='https://tieba.baidu.com/f?kw=%E8%83%B6%E5%B7%9E%E5%AE%9E%E9%AA%8C%E4%B8%AD%E5%AD%A6'
    start(url)


