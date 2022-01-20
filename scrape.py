import json

import requests
from lxml import etree
# import re
import logging
import sqlalchemy


# todo load schema for header and check

def getForumInfo(forumUrl: str) -> tuple:
    """
    获取贴吧页码数
    """
    res = requests.get(forumUrl)
    html = etree.HTML(res.text)
    nThread, nPost, nMember = html.xpath('//div[@class="th_footer_l"]/span[@class="red_text"][position()<=3]/text()')
    nThread = int(nThread)
    nPost = int(nPost)
    nMember = int(nMember)
    nPage = 1 + nThread // 50
    # n=re.search('(?<=pn=)\d+',href).group()
    return nPage, nThread, nPost, nMember


def getThreadList(pageUrl: str) -> list[dict, ...]:
    res = requests.get(pageUrl)
    logging.debug(f'{res.status_code=}')
    html = etree.HTML(res.text)
    ref = 'https://tieba.baidu.com/p/'

    title: list = html.xpath('//a[@class="j_th_tit "]/@title')
    nThread = len(title)
    logging.debug(f'{nThread=}')

    # href: list = html.xpath('//a[@class="j_th_tit "]/@href')
    threadId: list = html.xpath('//li[contains(@class," j_thread_list")]/@data-tid')
    logging.debug(f'{len(threadId)=}')

    url: list = [ref + u for u in threadId]
    # data:'//li[@class=" j_thread_list clearfix thread_item_box"]/@data-field'
    # data:'//li[@class=" j_thread_list thread_top j_thread_list clearfix thread_item_box"]/@data-field'
    # data[0] = {"id": 7674268841, "author_name": "Despair\u6cea\u6c34", "author_nickname": "kotone-",
    #            "author_portrait": "tb.1.98ff5db4.ADWlS2busR90robCMV09ZQ", "first_post_id": 142637365947,
    #            "reply_num": 63, "is_bakan": 'null', "vid": "", "is_good": 'null', "is_top": 'null', "is_protal": 'null',
    #            "is_membertop": 'null', "is_multi_forum": 'null', "frs_tpoint": 'null', "is_item_score": 'null',
    #            "is_works_info": 'null'}
    data: list = html.xpath('//li[contains(@class," j_thread_list")]/@data-field')

    dataJson: list = [json.loads(j) for j in data]
    firstPostId: list = [j['first_post_id'] for j in dataJson]
    createTime = [None] * nThread
    # author[0] = {"author_name": "Despair\u6cea\u6c34", "author_nickname": "kotone-",'id':'123'}
    # todo generate user table
    authorInfo: list[dict] = [
        {'name': j['author_name'],
         'nickname': j['author_nickname'],
         'id': j['author_portrait']}
        for j in dataJson]
    author = [i['id'] for i in authorInfo]

    logging.info(f'Got {len(title)} threads in page.')

    threadListInPage = []
    header = ("thread_title", "thread_id", "thread_url", "first_post_id", "thread_create_time", "thread_author")
    logging.debug('|'.join(header))
    for z in zip(title, threadId, url, firstPostId, createTime, author):
        # transfer lists to list(dict) : method 1
        threadInfo = dict(zip(header, z))
        logging.debug('|'.join(z))
        # transfer lists to list(dict) : method 2
        # threadInfo= {
        #     "thread_title": z[0],
        #     "thread_id":z[1],
        #     "thread_url": z[2],
        #     "first_post_id": z[3],
        #     "thread_create_time": None,
        #     "thread_author": z[5]
        # }

        threadListInPage.append(threadInfo)
        logging.debug(f'{len(threadListInPage)}')
        # todo sql

    return threadListInPage


def getPostAndComment(postUrl: str) -> tuple[list, list]:
    PAGE_MAGIC_NUMBER = 99999999
    nPage = PAGE_MAGIC_NUMBER

    postListInThread: list = []
    header = ("thread_id", "post_id", "post_no", "post_author", "post_create_time", "post_content")

    while nPage > 1:  # nPage=99999999:1 -> 3 -> 2 -> 1:pass
        res = requests.get(postUrl + f"pn={nPage}")  # nPage=99999999:1 -> 3 -> 2
        logging.debug(f'{res.status_code=}')
        html = etree.HTML(res.text)
        nPage -= 1  # nPage=99999998 -> 2 -> 1

        if nPage == PAGE_MAGIC_NUMBER - 1:  # nPage=99999998:in -> 2:pass -> 1:pass
            nPage = html.xpath('//li[@class="l_reply_num"]/span[@class="red"]/text()')[1]  # nPage=3

        # get posts list
        postId: list = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]/@data-pid')

        # data_field = {
        #     "author": {"user_id": 1368871114, "user_name": "\u5341\u4ebf\u5973\u6027\u7684\u5669\u68a6",
        #                "props": 'null',
        #                "portrait": "tb.1.63c823f2.l02W3izZIJJJTnSWEDAAxw?t=1544972491",
        #                "user_nickname": "\u6d6e\u751f\u82e5\u68a6\u00ba\u5929"},
        #     "content": {"post_id": 142600679911, "is_anonym": 'false', "forum_id": 6939271, "thread_id": 7670285611,
        #                 "content": "\u8fd8\u6709\u5c31\u662f\uff0c\u6b66\u5668\u7684\u7ee7\u627f\u673a\u5236\u662f\u600e\u6837\u7684\uff0c\u91cd\u65b0\u5f00\u6863\u662f\u4e0d\u662f\u5565\u90fd\u6ca1\u4e86",
        #                 "isPlus": 0, "builderId": 1368871114, "post_no": 2, "type": "0", "comment_num": 0, "is_fold": 0,
        #                 "props": 'null', "post_index": 1, "pb_tpoint": 'null'}}

        data: list = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]/@data-field')
        dataJson: list[dict] = [json.loads(j) for j in data]

        postNo: list = [j['content']['post_no'] for j in dataJson]
        authorInfo: list[dict] = [
            {'name': j['user_name'],
             'nickname': j['user_nickname'],
             'id': j['portrait']}
            for j in dataJson]
        author = [i['id'] for i in authorInfo]
        postTime: list = html.xpath('//div[@id="j_p_postlist"]/div[@data-pid]//span[@class="tail-info"][2]/text()')
        nPost = len(postId)
        threadId: list = [postUrl.replace('https://tieba.baidu.com/p/', '')] * nPost
        # todo originContent.getChildren()
        originContent: list = [j['content']['content'] for j in dataJson]

        # deal with post with pic or pic-emoji
        # <img class="BDE_Smiley" width="30" height="30" changedsize="false" src=url>
        # <img class="BDE_Image" pic_type="0" width="560" height="315" src=url size="209365">
        content = []
        # todo deal with inline url

        for c in originContent:

            if '<img class="BDE_' in c:
                h = etree.HTML(c)
                h.xpath('//img/@src')
                # todo and so on
                # insert pic location into text
                c: str  # =something
            c = c.replace('<br>', '')
            content.append(c)

        # iter postlist
        for z in zip(threadId, postId, postNo, author, postTime, content):
            # transfer lists to list(dict) : method 1
            postInfo = dict(zip(header, z))

            # transfer lists to list(dict) : method 2
            # threadInfo= {
            #     "thread_id": z[0],
            #     "post_id": z[1],
            #     "post_author":z[2],
            #     "post_create_time": z[3],
            #     "post_content": z[4],
            # }
            postListInThread.append(postInfo)

        # get list of post with comment
        # <div class="j_lzl_r p_reply" data-field=data_field></div>
        # data_field = {"pid": 142230521665, "total_num": 21}
        # data_field = {"pid": 142230521665, "total_num": "null"}
        # every 10 comments in a comment page
        commentDataField = html.xpath('//div[@class="j_lzl_r p_reply"]/@data-field')
        commentInfoList = [json.loads(j) for j in commentDataField if 'null' not in j]

        return postListInThread, commentInfoList


def getComment(tid, pid, nComment) -> list:
    """

    Args:
        tid: int: Thread ID
        pid: int: Post ID
        nComment: Number of comments

    Returns:
        commentListInPost: list: comment info in list
    """

    nPage = nComment // 10 + 1
    commentListInPost: list = []
    header = ("thread_id", "post_id", "comment_id", "comment_author", "comment_time", "comment_content", "comment_to")
    # data_field = {'pid': '142601876653', 'spid': '142644018196', 'user_name': '十亿女性的噩梦',
    #               'portrait': 'tb.1.63c823f2.l02W3izZIJJJTnSWEDAAxw', 'showname': '浮生若梦º天',
    #               'user_nickname': '浮生若梦º天'}

    # iter pages
    for n in range(1, 1 + nPage):
        # only if pn got right num, result shows.
        # start from pn=1 and get page num, then get other page
        commentUrl = f'https://tieba.baidu.com/p/comment?tid={tid}&pid={pid}&pn={nPage}'
        res = requests.get(commentUrl)
        logging.debug(f'{res.status_code=}')
        html = etree.HTML(res.text)

        threadId: list = [tid] * nComment
        postId: list = [pid] * nComment
        # data_field = {"spid": 142244133447, "showname": "\u9ed1\u8336\u7238\u7238\u2642", "user_name": "reny327",
        #               "portrait": "tb.1.b8e89c6b.tsi6-65LdMMa7xV2mhL9QA"}
        data = html.xpath('//li[contains(@class,"lzl_single_post j_lzl_s_p")]/@data-field')
        dataJson: list[dict] = [json.loads(j) for j in data]

        commentId: list = [j['spid'] for j in dataJson]

        authorInfo: list[dict] = [
            {'name': j['user_name'],
             'nickname': j['showname'],
             'id': j['portrait']}
            for j in dataJson]
        author = [i['id'] for i in authorInfo]

        postTime: list = html.xpath('//div[@class="lzl_content_reply"]/span[@class="lzl_time"]/text()')
        # todo deal with img
        originContent: list = html.xpath('//span[@class="lzl_content_main"]')
        content = []
        commentTo = []
        imgHolder = []

        # iter comments
        for c in originContent:
            # todo split into func: formatComtent(element,isComment)->content:str,commentTo
            # contentString = c.xpath('string(.)')
            textList = c.xpath('text()')
            textList = [t.strip() for t in textList]
            children = c.getchildren()
            # deal with reply
            if children[0].tag == 'a':
                # <a href="ref" onclick="func()" onmouseover="showattip(this)"
                # onmouseout="hideattip(this)" username=" "
                # portrait="tb.1.ea338836.j5UZxjq5UaG4aUh6mtuA_w"
                # target="_blank" class="at"> 我果然还是太天真</a>
                # del reply location
                to = children.pop(0)
                toName = to.text
                toID = to.get('portrait')

                toInfo = {'author_name': toName,
                          'author_nickname': '',
                          'id': toID
                          }
                imgHolder.append(toName)
            else:
                toID = ''

            nImg = len(children)
            for i in range(nImg):
                img = children[i]
                href = img.get('ref')
                # todo emoji dict
                imgType = img.get('class')
                re = requests.get(href)
                commentIndex = originContent.index(c)
                imgAddr = f'./img/{tid}-{pid}-{commentId[commentIndex]}-{i}.jpg'

                with open(imgAddr, 'wb') as f:
                    f.write(re.content)

            rawText = '%s'.join(textList)

            imgHolder += [f'<#{i}#>' for i in range(nImg)]
            formatContent = rawText % (tuple(imgHolder))
            content.append(formatContent)
            commentTo.append(toID)

        for z in zip(threadId, postId, commentId, author, postTime, content, commentTo):
            # transfer lists to list(dict) : method 1
            commentInfo = dict(zip(header, z))

            # transfer lists to list(dict) : method 2
            # commentInfo = {
            #     "thread_id": "thread_href",
            #     "post_id": "123",  # post no://div[@id="j_p_postlist"]/div[1]/@data-pid
            #     "comment_id": "123",
            #     "comment_time": "time",
            #     "comment_author": "author",
            #     "comment_content": "content",
            #     "comment_to": "to thread or to user"
            # }
            commentListInPost.append(commentInfo)

        return commentListInPost


def start(forumUrl):
    logging.info(f'Start to scraping {forumUrl}...')
    nPage, nThread, nPost, nMember = getForumInfo(forumUrl)
    logging.info(f'This forum has {nPage} pages, {nMember} posted {nPost} posts in {nThread} threads.')

    # "threadsPool": [
    #     {
    #         "thread_title": "<title>",
    #         "thread_href": "p/7579007237",
    #         "thread_id":"123",
    #         "first_post_id":"<post id>",
    #         "thread_create_time": "<time>",
    #         "thread_author": "<thread author>"
    #    }
    # ]
    threadsPool = []
    for n in range(nPage):
        logging.info(f'scraping {n}/{nPage} pages...')
        forumPageUrl = f'{forumUrl}&pn={50 * n}'
        logging.debug(f'{forumPageUrl=}')
        threadsPool += getThreadList(forumPageUrl)
        logging.info(f'Got {len(threadsPool)}/{nThread} threads.')

    postsPool = []
    commentsPool = []
    for threadInfo in threadsPool:
        threadUrl = threadInfo["thread_url"]
        threadTitle = threadInfo["thread_title"]
        threadId = threadInfo['thread_id']
        logging.info(f'scraping {threadTitle[:8]}... at {threadUrl}')
        posts, comments = getPostAndComment(threadUrl)
        postsPool += posts
        commentsPool += comments
        logging.info(f'Got {len(postsPool)}/{nPost} posts.')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: <%(funcName)s> - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    forumName = input('Name of forum')
    url = f'https://tieba.baidu.com/f?kw={forumName}'
    start(url)
