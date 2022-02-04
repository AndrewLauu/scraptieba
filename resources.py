sql_schema = {
    "info": {
        "name":"forum name",
        "url":"forum url",
        "nPage": " page number of forum",
        "nThread": " thread number in forum",
        "nPost": " post number in forum",
        "nMember": " member number of forum"
    },
    "thread": [
        {
            "title": "thread_title",
            "id": "thread_id",
            "url": "thread_url",
            "first_post_id": "first_post_id",
            "create_time": "thread_create_time",
            "author": "thread_author"
        }
    ],
    "post": [
        {
            "thread_id": "thread_id",
            "id": "post_id",
            "post_no": "post_no",
            "author": "post_author",
            "create_time": "post_create_time",
            "content": "post_content"
        }
    ],
    "comment": [
        {
            "thread_id": "thread_id",
            "post_id": "post_id",
            "id": "comment_id",
            "author": "comment_author",
            "comment_time": "comment_time",
            "content": "comment_content",
            "comment_to": "comment_to"
        }
    ],
    "user": [
        {
            "name": "Despair\u6cea\u6c34",
            "nickname": "kotone-",
            "id": "123"
        }
    ]
}

emojiDict = {
    "0": {
        "title": "呵呵",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f01.png"
    },
    "1": {
        "title": "哈哈",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f02.png"
    },
    "2": {
        "title": "吐舌",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f03.png"
    },
    "3": {
        "title": "啊",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f04.png"
    },
    "4": {
        "title": "酷",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f05.png"
    },
    "5": {
        "title": "怒",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f06.png"
    },
    "6": {
        "title": "开心",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f07.png"
    },
    "7": {
        "title": "汗",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f08.png"
    },
    "8": {
        "title": "泪",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f09.png"
    },
    "9": {
        "title": "黑线",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f10.png"
    },
    "10": {
        "title": "鄙视",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f11.png"
    },
    "11": {
        "title": "不高兴",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f12.png"
    },
    "12": {
        "title": "真棒",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f13.png"
    },
    "13": {
        "title": "钱",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f14.png"
    },
    "14": {
        "title": "疑问",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f15.png"
    },
    "15": {
        "title": "阴险",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f16.png"
    },
    "16": {
        "title": "吐",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f17.png"
    },
    "17": {
        "title": "咦",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f18.png"
    },
    "18": {
        "title": "委屈",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f19.png"
    },
    "19": {
        "title": "花心",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f20.png"
    },
    "20": {
        "title": "呼~",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f21.png"
    },
    "21": {
        "title": "笑眼",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f22.png"
    },
    "22": {
        "title": "冷",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f23.png"
    },
    "23": {
        "title": "太开心",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f24.png"
    },
    "24": {
        "title": "滑稽",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f25.png"
    },
    "25": {
        "title": "勉强",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f26.png"
    },
    "26": {
        "title": "狂汗",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f27.png"
    },
    "27": {
        "title": "乖",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f28.png"
    },
    "28": {
        "title": "睡觉",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f29.png"
    },
    "29": {
        "title": "惊哭",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f30.png"
    },
    "30": {
        "title": "升起",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f31.png"
    },
    "31": {
        "title": "惊讶",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f32.png"
    },
    "32": {
        "title": "喷",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f33.png"
    },
    "33": {
        "title": "爱心",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f34.png"
    },
    "34": {
        "title": "心碎",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f35.png"
    },
    "35": {
        "title": "玫瑰",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f36.png"
    },
    "36": {
        "title": "礼物",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f37.png"
    },
    "37": {
        "title": "彩虹",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f38.png"
    },
    "38": {
        "title": "星星月亮",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f39.png"
    },
    "39": {
        "title": "太阳",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f40.png"
    },
    "40": {
        "title": "钱币",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f41.png"
    },
    "41": {
        "title": "灯泡",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f42.png"
    },
    "42": {
        "title": "茶杯",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f43.png"
    },
    "43": {
        "title": "蛋糕",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f44.png"
    },
    "44": {
        "title": "音乐",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f45.png"
    },
    "45": {
        "title": "haha",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f46.png"
    },
    "46": {
        "title": "胜利",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f47.png"
    },
    "47": {
        "title": "大拇指",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f48.png"
    },
    "48": {
        "title": "弱",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f49.png"
    },
    "49": {
        "title": "OK",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f50.png"
    },
    "50": {
        "title": "伤心",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f51.gif"
    },
    "51": {
        "title": "加油",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f52.gif"
    },
    "52": {
        "title": "必胜",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f53.gif"
    },
    "53": {
        "title": "期待",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f54.gif"
    },
    "54": {
        "title": "牛逼",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f55.gif"
    },
    "55": {
        "title": "胜利",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f56.gif"
    },
    "56": {
        "title": "跟丫死磕",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f57.gif"
    },
    "57": {
        "title": "踢球",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f58.gif"
    },
    "58": {
        "title": "面壁",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f59.gif"
    },
    "59": {
        "title": "顶",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f60.gif"
    },
    "60": {
        "title": "巴西怒",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f61.gif"
    },
    "61": {
        "title": "伴舞",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f62.gif"
    },
    "62": {
        "title": "奔跑",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f63.gif"
    },
    "63": {
        "title": "点赞手",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f64.gif"
    },
    "64": {
        "title": "加油",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f65.gif"
    },
    "65": {
        "title": "哭泣",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f66.gif"
    },
    "66": {
        "title": "亮红牌",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f67.gif"
    },
    "67": {
        "title": "球迷",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f68.gif"
    },
    "68": {
        "title": "耶",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f69.gif"
    },
    "69": {
        "title": "转屁股",
        "data-surl": "http://tb2.bdstatic.com/tb/editor/images/face/i_f70.gif"
    }
}

flow_schema = [
    {
        "thread_title": "<title>",
        "thread_id": "123",
        "url": "p/7579007237",
        "first_post_id": "first_post_id",
        "thread_create_time": "<time>",
        "thread_author": "<thread author>",
        "thread_post": [
            {
                "thread_id": "thread_id",
                "post_id": "123",
                "post_no": "post_no",
                "post_author": "<author>",
                "post_create_time": "<time>",
                "post_content": "12",
                "post_comment": [
                    {
                        "comment_id": "123",
                        "comment_time": "time",
                        "comment_author": "author",
                        "comment_content": "content",
                        "comment_to": "to thread or to user"
                    }
                ]
            }
        ]
    }
]
