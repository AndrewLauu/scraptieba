import json
import os.path
import uuid
import random
import time
import requests
from lxml import etree
import logging
from datetime import datetime

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

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)

# init root logger by setting basicConfig
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s.%(funcName)s [%(levelname)s]: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    handlers=[fileHandler, consoleHandler],
    encoding='utf8'
)

# Global log for this module
logger = logging.getLogger(__name__)

from SQLHandler import Info, Thread, Post, Comment, User, session, select, insertOrUpdate as insert
from resources import *


def getForumInfo(forumUrl: str) -> tuple[int, int, int, int]:
    """
    Get base info of forum
    Args:
        forumUrl: URL format string of forum

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
    logger.info(f'{forumUrl} has {nPage} pages, {nMember} users posted {nPost} posts in {nThread} threads.')

    return nPage, nThread, nPost, nMember


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

    def img(child) -> str:
        # img = children[i]
        href = child.get('src')
        res = requests.get(href)
        uid = uuid.uuid3(uuid.NAMESPACE_URL, href)
        imgAddr = f'./img/{threadId}/{postId}/'
        if commentId:
            imgAddr += f'{commentId}/'

        if not os.path.isdir(imgAddr):
            os.makedirs(imgAddr)

        imgName = f'{uid}.jpg'
        imgAddr += imgName
        with open(imgAddr, 'wb') as f:
            f.write(res.content)
        logger.info(f'Img saved at {imgAddr}')
        return f'[{imgName}]'

    def emoji(child) -> str:
        url: str = child.get('src')
        id: str = url.split('/')[-1].split('.')[0].replace('image_emoticon', '').replace('i_f', '').lstrip('0')
        emoName: str = emojiDict[id]["title"]
        return f'[{emoName}]'

    def reply(child) -> str:
        toName = child.text.strip()
        # toID = child.get('portrait')

        toInfo = {'name': toName,
                  'nickname': '',
                  'id': toID[:22]
                  }
        insert(User, [toInfo])
        return toName

    def br(child) -> str:
        return "\n"

    def inlineUrl(child) -> str:
        return child.text.strip()

    formatContent: str = ''
    toID: str = ''

    caseType: dict = {
        'BDE_Image': img,
        'BDE_Smiley': emoji,
        'j-no-opener-url': inlineUrl,
        'at': reply,
        None: br
    }

    children = element.xpath('node()')
    logger.debug('-' * 10)
    logger.debug(f'{children}')

    for child in children:
        if isinstance(child, str):
            formatChild: str = child.strip()
        else:
            classAttr: str = child.get('class')
            if not toID:
                toID = child.get('portrait')
            formatChild = caseType[classAttr](child)
            # logger.debug(formatChild)
            logger.debug(f'{child}: {classAttr}-> {formatChild}')

        formatContent += formatChild

    logger.debug(formatContent)
    return formatContent, toID


def getThreadList(pageUrl: str) -> list[dict]:
    """
    Get threads in specific page url
    Args:
        pageUrl: Url

    Returns:
        threadListInPage: List of threads info, thread info are structured in resources.sql_schema['thread']
    """
    res = requests.get(pageUrl)

    html = etree.HTML(res.text)

    title: list[str] = html.xpath('//a[@class="j_th_tit "]/@title')
    nThread: int = len(title)
    logger.info(f'Found {nThread} threads in this page')

    threadId: list[str] = html.xpath('//li[contains(@class," j_thread_list")]/@data-tid')
    threadId: list[int] = [int(id) for id in threadId]

    ref: str = 'https://tieba.baidu.com/p'
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
    # use fake date to insert and change to true time in last
    createTime: list[datetime] = [datetime(2021, 1, 1, 0, 0, 0)] * nThread

    # author[0] = {"author_name": "Despair\u6cea\u6c34", "author_nickname": "kotone-",'id':'123'}
    authorInfo: list[dict] = [
        {'name': j['author_name'],
         'nickname': j['author_nickname'],
         'id': j['author_portrait'][:22]}
        for j in dataJson]
    author: list[str] = [i['id'] for i in authorInfo]
    insert(User, authorInfo)

    threadListInPage: list[dict] = []

    header: list = sql_schema['thread'][0].keys()
    logger.debug('|'.join(header))

    for z in zip(title, threadId, urls, firstPostId, createTime, author):
        threadInfo: dict = dict(zip(header, z))
        logger.debug('|'.join([str(z_) for z_ in z]))

        threadListInPage.append(threadInfo)
    return threadListInPage


def getPostsInfo(threadUrl: str) -> tuple[list, list]:
    """
    Get posts in specific thread and post id with comments in thread
    Args:
        threadUrl: Url
    Returns:
        postListInThread: List of posts info, posts info are structured in resources.sql_schema['post']
        commentInfo: dicts containing post id and comment number in list
    """

    # We goto page 1 and get max page number
    maxPage: int = 99999999
    nPage: int = 1

    postListInThread: list[dict] = []
    header: list = sql_schema['post'][0].keys()

    commentInfo: list[dict] = []

    while nPage <= maxPage:
        t = random.randint(1, 5)
        logger.info(f'Sleeping {t} s...')
        time.sleep(t)
        res = requests.get(threadUrl + f"?pn={nPage}")
        html = etree.HTML(res.text)

        # Get real page num
        if nPage == 1:
            maxPage = int(html.xpath('//li[@class="l_reply_num"]/span[@class="red"]/text()')[1])  # nPage=3
            logger.info(f'{maxPage} page(s) in this thread')

        # get posts list
        postId: list[str] = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]/@data-pid')
        postId: list[int] = [int(id) for id in postId]
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
        dataJson: list[dict] = [json.loads(j) for j in data]

        postNo: list[int] = [int(j['content']['post_no']) for j in dataJson]
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
        postTime: list[str] = html.xpath(
            '//div[@id="j_p_postlist"]/div[@data-pid]//span[@class="tail-info"][last()]/text()')
        createTime: list[datetime] = [datetime.strptime(t, "%Y-%m-%d %H:%M") for t in postTime]
        tid: int = int(threadUrl.replace('https://tieba.baidu.com/p/', ''))
        threadId: list[int] = [tid] * nPost

        # originContent: list = [j['content']['content'] for j in dataJson]
        originContent: list[etree._Element] = html.xpath('//div[@class="d_post_content j_d_post_content "]')
        content: list[str] = []
        for c in originContent:
            pid: int = postId[originContent.index(c)]
            content.append(getFormatContent(c, tid, pid)[0])

        logger.debug('|'.join(header))
        # iter postlist
        for z in zip(threadId, postId, postNo, author, createTime, content):
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


def getComment(tid: int, pid: int, nComment: int) -> list[dict]:
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
        for z in zip(threadId, postId, commentId, author, createTime, content, commentTo):
            commentInfo = dict(zip(header, z))
            commentListInPost.append(commentInfo)
            logger.debug('|'.join([str(z_) for z_ in z]))

    return commentListInPost


def start(forumName: str = None, forumUrl: str = None):
    logger.debug(f'{forumName=}, {forumUrl=}')

    if not forumName and not forumUrl:
        logger.error('Forum name and url should be specified one')
        raise ValueError('Forum name and url should be specified one')
    elif forumName and forumUrl:
        forumUrl: str = f'https://tieba.baidu.com/f?kw={forumName}'
        logger.warning(f'Forum name and url can only be specified one, use {forumName=}->{forumUrl=}')
    elif forumName:
        forumUrl: str = f'https://tieba.baidu.com/f?kw={forumName}'
    else:
        forumName: str = forumUrl.split('?')[-1].split('&')[0].replace('kw=', '')

    logger.info(f'Start to scraping {forumName} at {forumUrl}...')
    # get base info
    nPage, nThread, nPost, nMember = getForumInfo(forumUrl)

    # insert info into db
    header: list = sql_schema['info'].keys()
    logger.debug('|'.join(header))

    info: dict[str:int] = dict(zip(
        header,
        (forumName, forumUrl, nPage, nThread, nPost, nMember)
    ))
    insert(Info, info)

    # get threads in forum
    threadsPool: list[dict] = []

    # iter pages, append threads into pool
    for n in range(nPage):
        logger.info(f'scraping {n}/{nPage} pages...')

        forumPageUrl: str = f'{forumUrl}&pn={50 * n}'
        threadsPool += getThreadList(forumPageUrl)
        logger.info(f'Got {len(threadsPool)}/{nThread} threads.')
        logger.info('Sleeping...')
        time.sleep(random.randint(1, 5))

    insert(Thread, threadsPool)

    # iter threads, get posts and comment info in each thread and append into pool
    postsPool: list = []
    commentsPool: list = []
    for threadInfo in threadsPool:
        threadUrl: str = threadInfo["thread_url"]
        threadTitle: str = threadInfo["thread_title"][:8]
        threadId: int = threadInfo['thread_id']
        logger.info(f'scraping {threadTitle}... at {threadUrl}')
        posts, commentsInfo = getPostsInfo(threadUrl)
        postsPool += posts

        logger.info(f'Got {len(postsPool)}/{nPost} posts.')
        # commentInfo = [{"pid": 142230521665, "total_num": 21}]
        nComment: int = len(commentsInfo)
        for i in commentsInfo:
            comments = getComment(threadId, *i)
            commentsPool += comments
            logger.info(f'Got {len(commentsPool)}/{nComment} comments in {threadTitle}:{i["pid"]}')

            logger.info('Sleeping...')
            time.sleep(random.randint(1, 5))

    insert(Post, postsPool)
    insert(Comment, commentsPool)

    threads = session.execute(select(Thread)).all()
    for thread in threads:
        thread = thread[0]
        thread.create_time = thread.firstPost.create_time
    session.commit()


if __name__ == '__main__':
    logger.debug('Init by running main module')
    forumName: str = input('Name of forum: ').strip()
    if forumName:
        logger.debug(f'{forumName=}')
        start(forumName=forumName)
        session.close()
    else:
        logger.error('Forum name is not specified')
        raise ValueError('Forum name is not specified')
