import json
import logging
import os.path
import random
import sys
import time
import uuid
from datetime import datetime

import requests
from lxml import etree

from resources import *

# Global setting for log for all module
# method 1
# init root logger
# rootLogger = logging.getLogger()
# set formatter
# format = logging.Formatter(
#     fmt='%(asctime)s %(levelname)s: %(module)s.%(funcName)s - %(message)s',
#     datefmt='%Y/%m/%d %H:%M:%S')
# set handler with format
# fh = logging.FileHandler('log.log')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(format)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# ch.setFormatter(format)
# add handler to root logger
# rootLogger.addHandler(fh)
# rootLogger.addHandler(ch)

# method 2
# set handler
fileHandler = logging.FileHandler('log.log')
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.INFO)

# init root logger by setting basicConfig
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s.%(funcName)s [%(levelname)s]: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    handlers=[fileHandler, consoleHandler],
    encoding='utf8'
)

from SQLHandler import session, Forum, Thread, Post, Comment, User, select, insertOrUpdate as insert

# Global log for this module
logger: logging.Logger = logging.getLogger(__name__)


def getForumId(forumName: str) -> int:
    api: str = f'http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname={forumName}'
    forumId: int = requests.get(api).json()['data']['fid']
    return forumId


def getForumInfo(forumName: str, forumUrl: str) -> tuple[int, ...]:
    """
    Get base info of forum
    Args:
        forum_url: URL format string of forum

    Returns:
        nPage: page number of forum
        nThread: thread number in forum
        nPost: post number in forum
        nMember: member number of forum
    """

    res = requests.get(forumUrl)
    html = etree.HTML(res.text)

    nThread, nPost, nMember = html.xpath('//div[@class="th_footer_l"]/span[@class="red_text"][position()<=3]/text()')
    nThread: int = int(nThread)
    nPost: int = int(nPost)
    nMember: int = int(nMember)
    nPage: int = 1 + (nThread - 1) // 50
    slogan: str = html.xpath('//p[@class="card_slogan"]//text()')[0]
    logger.info(f'{forumUrl} has {nPage} pages, {nMember} users posted {nPost} posts in {nThread} threads.')

    forumId: int = getForumId(forumName)
    # insert info into db
    header: list[str] = sql_schema['info'].keys()
    logger.debug('|'.join(header))

    info: dict[str:int | str] = dict(zip(
        header,
        (forumId, forumName, forumUrl, nPage, nThread, nPost, nMember, slogan)
    ))
    insert(Forum, info)

    return forumId, nPage, nThread, nPost, nMember


def getFormatContent(element, threadId: int = None, postId: int = None, commentId: int = None) -> tuple[
    str, str]:
    """
    deal with img, inline url, reply<a>,<br> in content
    1. img:
        <img class="BDE_Image" src=url size="417991" changedsize="true" width="560" height="553">
        return format text with img id and download img
    2. pic-emoji:
        <img class="BDE_Smiley" width="30" height="30" changedsize="false" src=url>
        return format text with emoji name
    3. inline url:
        <a href=jump url target="_blank" rel="noopener noreferrer nofollow" class="j-no-opener-url">shown url</a>
        return raw text url
    4. reply:
        <a href=broken url onclick="func()" onmouseover="showattip(this)"
        onmouseout="hideattip(this)" username=" "
        portrait="tb.1.ea338836.j5UZxjq5UaG4aUh6mtuA_w"
        target="_blank" class="at"> text </a>
        return
    5. br
        <br>
        return \n

    Args:
        element: xpath element

        threadId: thread id
        postId: post id
        commentId: comment id ignorable

    Returns:
        formatted content: str
        user id replied to: str or None if not a reply
    """

    # contentString = element.xpath('string(.)')

    # textList = element.xpath('text()')
    # logger.debug(f'{textList}')
    # textList = [t.strip() for t in textList]
    # children = element.getchildren()

    # if not children:
    #     return textList[0], None

    def saveFile(filename: str, url: str = None, html: str = None):
        flag = ''
        if url:
            html = requests.get(url).content
            flag = 'b'

        path = os.path.dirname(filename)

        if not os.path.isdir(path):
            os.makedirs(path)

        with open(filename, 'w' + flag) as f:
            f.write(html)
        logger.info(f'File saved at {filename}')

    def img(childEle) -> str:
        # img = children[i]
        href: str = childEle.get('src')
        imgFormat = href.split('.')[-1]
        uid = uuid.uuid3(uuid.NAMESPACE_URL, href)
        imgAddr = f'./media/{threadId}/{postId}/'
        if commentId:
            imgAddr += f'{commentId}/'

        imgName = f'{uid}.{imgFormat}'
        imgAddr += imgName
        saveFile(url=href, filename=imgAddr)
        return f'[{imgName}]'

    def emoji(childEle) -> str:
        url: str = childEle.get('src')
        emojiId: str = url.split('/')[-1].split('.')[0].replace('image_emoticon', '').replace('i_f', '').lstrip('0')
        emoName: str = emojiDict[emojiId]["title"]
        return f'[{emoName}]'

    def reply(childEle) -> str:
        toName = childEle.text.strip()
        # toID = child.get('portrait')

        toInfo = {'name': toName,
                  'nickname': '',
                  'id': toID[:22]
                  }
        insert(User, [toInfo])
        return toName

    def br(childEle) -> str:
        return "\n"

    def inlineUrl(childEle) -> str:
        return childEle.text.strip()

    def video(childEle) -> str:
        href: str = childEle.getchildren()[0].get('data-video')
        uid = uuid.uuid3(uuid.NAMESPACE_URL, href)
        vFormat = href.split('?')[0].split('.')[-1]
        vName = f'{uid}.{vFormat}'
        vAddr = f'./media/{threadId}/{postId}/{vName}'
        saveFile(url=href, filename=vAddr)
        return f'[{vName}]'

    def invalid(childEle) -> str:
        html: str = etree.tostring(childEle, pretty_print=True, encoding='utf8', with_comments=True)
        uid = uuid.uuid3(uuid.NAMESPACE_URL, 'www.example.com')
        htmlAddr = f'./media/{threadId}/{postId}/'
        if commentId:
            htmlAddr += f'{commentId}/'

        htmlName = f'{uid}.html'
        htmlAddr += htmlName
        saveFile(filename=htmlAddr, html=html)
        return f'Not supported rich text {htmlName}'

    formatContent: str = ''
    toID: str = ''

    caseType: dict = {
        'BDE_Image': img,
        'BDE_Smiley': emoji,
        'j-no-opener-url': inlineUrl,
        'at': reply,
        'video_src_wrapper': video,
        None: br
    }

    children = element.xpath('node()')
    logger.debug('-' * 10)
    logger.debug(f'{children}')

    for child in children:
        if isinstance(child, str):
            formatChild: str = child.strip()
            classAttr = 'str'
        else:
            classAttr: str = child.get('class')
            if not toID:
                toID = child.get('portrait')
            formatChild = caseType.get(classAttr, invalid)(child)
        logger.debug(f'{child}: {classAttr}-> {formatChild}')

        formatContent += formatChild

    logger.debug(formatContent)
    return formatContent, toID


def getThreadList(forumUrl: str, pageFrom: int = 1, pageTo: int = 1, dynamicPageTo: bool = True) -> list[
    dict]:
    """
    Get threads in specific page url
    Args:
        pageFrom:
        pageTo:
        pageUrl: Url

    Returns:
        threadListInPage: List of threads info, thread info are structured in resources.sql_schema['thread']
    """

    # get threads in forum
    threadList: list[dict] = []
    header: list[str] = sql_schema['thread'][0].keys()
    ref: str = 'https://tieba.baidu.com/p'

    for pn in range(pageFrom - 1, pageTo):
        interval: int = random.randint(1, 5)
        logger.info(f'Sleeping {interval} s...')
        time.sleep(interval)

        logger.info(f'scraping {pn}/{pageTo - pageFrom + 1} pages...')
        pageUrl: str = f'{forumUrl}&pn={50 * pn}'

        res = requests.get(pageUrl)
        html = etree.HTML(res.text)

        title: list[str] = html.xpath('//a[@class="j_th_tit "]/@title')

        nForumThread: int = int(html.xpath('//div[@class="th_footer_l"]/span[@class="red_text"][1]/text()'))
        nForumPage: int = 1 + (nForumThread - 1) // 50

        # every page in forum except the last page has 50 threads
        # last page has uncertain quantity, to scrape = total thread - unused leading pages * 50
        if pageTo == nForumPage:
            nThread: int = nForumThread - (pageFrom - 1) * 50
        else:
            nThread: int = (pageTo - pageFrom + 1) * 50

        nPageThread: int = len(title)
        logger.info(f'Found {nPageThread}/{nThread} threads in this page')

        threadId: list[str] = html.xpath('//li[contains(@class," j_thread_list")]/@data-tid')
        threadId: list[int] = [int(tid) for tid in threadId]

        urls: list[str] = [f'{ref}/{u}' for u in threadId]
        # data:'//li[@class=" j_thread_list clearfix thread_item_box"]/@data-field'
        # data:'//li[@class=" j_thread_list thread_top j_thread_list clearfix thread_item_box"]/@data-field'
        # data[0] = {"id": 7674268841, "author_name": "Despair\u6cea\u6c34", "author_nickname": "kotone-",
        #            "author_portrait": "tb.1.98ff5db4.ADWlS2busR90robCMV09ZQ", "first_post_id": 142637365947,
        #            "reply_num": 63, "is_bakan": 'null', "vid": "", "is_good": 'null', "is_top": 'null', "is_protal": 'null',
        #            "is_membertop": 'null', "is_multi_forum": 'null', "frs_tpoint": 'null', "is_item_score": 'null',
        #            "is_works_info": 'null'}
        data: list[str] = html.xpath('//li[contains(@class," j_thread_list")]/@data-field')
        dataJson: list[dict] = [json.loads(j) for j in data]
        firstPostId: list[int] = [int(j['first_post_id']) for j in dataJson]

        # use place-holding date to insert and change to true time in last
        createTime: list[datetime] = [datetime(2021, 1, 1, 0, 0, 0)] * nPageThread

        # author[0] = {"author_name": "Despair\u6cea\u6c34", "author_nickname": "kotone-",'id':'123'}
        authorInfo: list[dict[str:str]] = [
            {
                'name': j['author_name'],
                'nickname': j['author_nickname'],
                'id': j['author_portrait'][:22]
            }
            for j in dataJson
        ]
        author: list[str] = [i['id'] for i in authorInfo]
        insert(User, authorInfo)

        forumId: int = getForumId(html.xpath('//input[@id="wd2"]/@value'))
        fid: list[int] = [forumId] * nPageThread

        logger.debug('|'.join(header))
        for z in zip(fid, title, threadId, urls, firstPostId, createTime, author):
            threadInfo: dict = dict(zip(header, z))
            logger.debug('|'.join([str(z_) for z_ in z]))
            threadList.append(threadInfo)

        logger.info(f'Got {len(threadList)}/{nThread} threads.')

    return threadList


def getPosts(threadUrl: str) -> tuple[list[dict], list[dict]]:
    """
    Get posts in specific thread and post id with comments in thread
    Args:
        threadUrl: Url
    Returns:
        postListInThread: List of posts info, posts info are structured in resources.sql_schema['post']
        commentInfo: dicts containing post id and comment number in list
    """

    # goto page 1 and get max page number
    maxPage: int = 99_999_999
    nPage: int = 1

    postListInThread: list[dict] = []
    header: list = sql_schema['post'][0].keys()

    commentInfo: list[dict] = []

    while nPage <= maxPage:
        interval: int = random.randint(1, 5)
        logger.info(f'Sleeping {interval} s...')
        time.sleep(interval)
        res = requests.get(threadUrl + f"?pn={nPage}")
        html = etree.HTML(res.text)

        # Get real page num
        if nPage == 1:
            maxPage = int(html.xpath('//li[@class="l_reply_num"]/span[@class="red"]/text()')[1])  # nPage=3
            logger.info(f'{maxPage} page(s) in this thread')

        # get posts list
        postId: list[str] = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]/@data-pid')
        postId: list[int] = [int(pid) for pid in postId]
        nPost: int = len(postId)

        logger.info(f'Got {nPost} posts in this {nPage} / {maxPage} pages')

        # data_field = {
        #     "author": {"user_id": 1368871114, "user_name": "\u5341\u4ebf\u5973\u6027\u7684\u5669\u68a6",
        #                "props": 'null',
        #                "portrait": "tb.1.63c823f2.l02W3izZIJJJTnSWEDAAxw?t=1544972491",
        #                "user_nickname": "\u6d6e\u751f\u82e5\u68a6\u00ba\u5929"},
        #     "content": {"post_id": 142600679911, "is_anonym": 'false', "forum_id": 6939271, "thread_id": 7670285611,
        #                 "content": "\u8fd8\u6709\u5c31\u662f\uff0c\u6b66\u5668\u7684\u7ee7\u627f\u673a\u5236\u662f\u600e\u6837\u7684\uff0c\u91cd\u65b0\u5f00\u6863\u662f\u4e0d\u662f\u5565\u90fd\u6ca1\u4e86",
        #                 "isPlus": 0, "builderId": 1368871114, "post_no": 2, "type": "0", "comment_num": 0, "is_fold": 0,
        #                 "props": 'null', "post_index": 1, "pb_tpoint": 'null'}}

        data: list[str] = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]/@data-field')
        dataJson: list[dict[str:int | str]] = [json.loads(j) for j in data]
        fid: list[int] = [dataJson[0]['content']['forum_id']] * nPost

        postNo: list[int] = [int(j['content']['post_no']) for j in dataJson]
        postIndex: list[int] = [int(j['content']['post_index']) for j in dataJson]
        logger.debug('Inserting users to User')
        authorInfo: list[dict] = [
            {
                'name': j['author']['user_name'],
                'nickname': j['author']['user_nickname'],
                'id': j['author']['portrait'][:22]
            }
            for j in dataJson
        ]
        insert(User, authorInfo)
        author: list[str] = [i['id'] for i in authorInfo]

        origins: list[str] = []
        createTime: list[datetime] = []

        tails: list[etree._Element] = html.xpath('//div[@class="post-tail-wrap"]')
        for tail in tails:
            tailSpan: list[etree._Element] = tail.xpath('./span[@class="tail-info"]')

            postTime: datetime = datetime.strptime(tailSpan[-1].text, "%Y-%m-%d %H:%M")
            createTime.append(postTime)

            origin: str = ''
            if len(tailSpan) == 3:
                origin = tailSpan[0].findtext('./a')
            origins.append(origin)

        tid: int = int(threadUrl.replace('https://tieba.baidu.com/p/', ''))
        threadId: list[int] = [tid] * nPost

        # originContent: list = [j['content']['content'] for j in dataJson]
        originContent: list[etree._Element] = html.xpath('//div[@class="d_post_content j_d_post_content "]')
        content: list[str] = []
        for n, c in enumerate(originContent):
            content.append(getFormatContent(c, tid, postId[n])[0])

        logger.debug('|'.join(header))
        # iter postlist
        for z in zip(fid, threadId, postId, postNo, postIndex, author, createTime, content, origins):
            logger.debug('|'.join([str(z_) for z_ in z]))
            postInfo: dict = dict(zip(header, z))
            postListInThread.append(postInfo)

        # get list of post with comment
        # <div class="j_lzl_r p_reply" data-field=data_field></div>
        # data_field = {"pid": 142230521665, "total_num": 21}
        # data_field = {"pid": 142230521665, "total_num": "null"}
        # every 10 comments in a comment page
        commentDataField: list[str] = html.xpath('//div[@class="j_lzl_r p_reply"]/@data-field')
        commentInfo += [json.loads(j) for j in commentDataField if 'null' not in j]
        logger.info(f'Got {len(commentInfo)} comments in {nPage} / {maxPage}')

        nPage += 1  # nPage=99999998 -> 2 -> 1

    return postListInThread, commentInfo


def getComment(forumId: int, tid: int, pid: int, nComment: int) -> list[dict]:
    """
    get comments to a post
    Args:
        tid: int: Thread ID
        pid: int: Post ID
        nComment: Number of comments

    Returns:
        commentListInPost: list: comments' info in list
    """
    # 1:1, 9:1, 10:1, 11:2
    nPage = 1 + (nComment - 1) // 10
    commentListInPost: list[dict] = []
    header = sql_schema['comment'][0].keys()
    # data_field = {'pid': '142601876653', 'spid': '142644018196', 'user_name': '十亿女性的噩梦',
    #               'portrait': 'tb.1.63c823f2.l02W3izZIJJJTnSWEDAAxw', 'showname': '浮生若梦º天',
    #               'user_nickname': '浮生若梦º天'}

    # iter pages
    for n in range(1, 1 + nPage):
        # only if pn got right num, result shows.
        # start from pn=1 and get page num, then get other page
        commentsUrl = f'https://tieba.baidu.com/p/comment?tid={tid}&pid={pid}&pn={nPage}'
        res = requests.get(commentsUrl)
        html = etree.HTML(res.text)

        threadId: list[int] = [tid] * nComment
        postId: list[int] = [pid] * nComment
        fid: list[int] = [forumId] * nComment

        # data_field = {"spid": 142244133447, "showname": "\u9ed1\u8336\u7238\u7238\u2642", "user_name": "reny327",
        #               "portrait": "tb.1.b8e89c6b.tsi6-65LdMMa7xV2mhL9QA"}
        data = html.xpath('//li[contains(@class,"lzl_single_post j_lzl_s_p")]/@data-field')
        dataJson: list[dict] = [json.loads(j) for j in data]

        commentId: list[int] = [int(j['spid']) for j in dataJson]

        authorInfo: list[dict] = [
            {
                'name': j['user_name'],
                'nickname': j['showname'],
                'id': j['portrait'][:22]
            }
            for j in dataJson
        ]
        logger.debug('Inserting users into User')
        insert(User, authorInfo)
        author: list[str] = [i['id'] for i in authorInfo]

        postTime: list = html.xpath('//div[@class="lzl_content_reply"]/span[@class="lzl_time"]/text()')
        createTime: list[datetime] = [datetime.strptime(t, "%Y-%m-%d %H:%M") for t in postTime]

        originContent: list = html.xpath('//span[@class="lzl_content_main"]')
        content: list[str] = []
        commentTo: list[str] = []

        for c in originContent:
            cid: int = commentId[originContent.index(c)]
            formatContent, toID = getFormatContent(c, tid, pid, cid)
            content.append(formatContent)
            commentTo.append(toID)

        logger.debug('|'.join(header))
        for z in zip(fid, threadId, postId, commentId, author, createTime, content, commentTo):
            commentInfo = dict(zip(header, z))
            commentListInPost.append(commentInfo)
            logger.debug('|'.join([str(z_) for z_ in z]))

    return commentListInPost


def start(name: str = None, url: str = None):
    logger.debug(f'Got params {name=}, {url=}')

    # forum name or forum url
    # name and url
    if not name and not url:
        logger.error('Forum name and url should be specified one')
        raise ValueError('Forum name and url should be specified one')

    # name | name and url
    elif name:
        # not url
        forumName: str = name.rstrip('吧')
        forumUrl: str = f'https://tieba.baidu.com/f?kw={name}'
        # and url
        if url:
            logger.warning(f'Forum name and url can only be specified one, url ignored, use {name=}->{forumUrl=}')

    # url
    else:
        # deal with unless param in url
        forumUrl = url.split('&')[0]
        forumName = forumUrl.split('?')[-1].lstrip('kw=')

    logger.info(f'Start to scraping {forumName} at {forumUrl}...')
    # get base info
    fid, nPage, nThread, nPost, nMember = getForumInfo(forumName, forumUrl)

    # get thread list in forum
    threadsPool: list[dict] = getThreadList(forumUrl=forumUrl, pageTo=nPage)
    insert(Thread, threadsPool)

    # iter threads, get posts and comment info in each thread and append into pool
    nPostGot: int = 0
    commentsInfoPool: list[dict] = []
    for threadInfo in threadsPool:
        threadUrl: str = threadInfo["thread_url"]
        threadTitle: str = threadInfo["thread_title"][:7]
        threadId: int = threadInfo['thread_id']
        logger.info(f'scraping {threadTitle}... at {threadUrl}')
        posts, commentsInfo = getPosts(threadUrl=threadUrl)
        nPostGot += len(posts)
        insert(Post, posts)
        logger.info(f'Got {nPostGot}/{nPost} posts.')

        for ci in commentsInfo:
            ci.update({
                'tid': threadId,
                'nComment': ci['total_num']
            })
            ci.pop('total_num')
        commentsInfoPool += commentsInfo

    commentsPool: list[dict] = []
    # commentInfo = {"pid": 142230521665, "nComment": 21, "tid" : 73412545}
    for commentsInfo in commentsInfoPool:
        comments = getComment(forumId=fid, **commentsInfo)
        commentsPool += comments
        logger.info(
            f'Got {len(commentsPool)}/{len(commentsInfoPool)} comments in {commentsInfo["tid"]}:{commentsInfo["pid"]}')

        interval: int = random.randint(1, 5)
        logger.info(f'Sleeping {interval} s...')
        time.sleep(interval)

    insert(Comment, commentsPool)

    # change thread create time from placeholder to real time
    threads = session.execute(select(Thread)).all()
    for thread in threads:
        thread = thread[0]
        thread.create_time = thread.firstPost.create_time
    session.commit()
    session.close()


if __name__ == '__main__':
    logger.debug('Init from __main__')
    ioForumName: str = input('Name of forum: ').strip()
    if ioForumName:
        logger.debug(f'Input: {ioForumName}')
        start(name=ioForumName)
    else:
        logger.error('Forum name is not specified')
        raise ValueError('Forum name is not specified')
