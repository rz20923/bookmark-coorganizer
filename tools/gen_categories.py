# -*- coding: utf-8 -*-
"""生成面向整个互联网的通用分类规则库 categories.json

设计:
- 通用大类覆盖全互联网常见站点类型（约 20 个）
- 通用域名映射：数百个主流站点（中文互联网 + 国际主流）
- 旧规则（从 classify.py 提取的 385 域名）按映射迁移到新大类体系
- 通用兜底关键词：按主题正则覆盖，未命中再走自适应聚类
"""
import json
import re
import sys

# ---------------- 通用大类（顺序即输出顺序） ----------------
CATS = [
    "搜索与门户", "新闻资讯", "社交与社区", "视频与直播", "音乐与音频",
    "游戏与电竞", "购物与电商", "美食与生活", "旅游与出行", "医疗与健康",
    "教育与学习", "金融与理财", "办公与协作", "开发与编程", "AI 人工智能",
    "设计与创意", "工具与效率", "网盘与存储", "阅读与知识", "壁纸与美化",
    "政府与公共", "其他",
]

# ---------------- 通用域名映射：域名 -> [大类, 二级分类] ----------------
GENERIC = {
    # ==== 搜索与门户 ====
    "baidu.com": ["搜索与门户", "搜索引擎"], "google.com": ["搜索与门户", "搜索引擎"],
    "google.com.hk": ["搜索与门户", "搜索引擎"], "bing.com": ["搜索与门户", "搜索引擎"],
    "cn.bing.com": ["搜索与门户", "搜索引擎"], "sogou.com": ["搜索与门户", "搜索引擎"],
    "so.com": ["搜索与门户", "搜索引擎"], "sm.cn": ["搜索与门户", "搜索引擎"],
    "duckduckgo.com": ["搜索与门户", "搜索引擎"], "yandex.com": ["搜索与门户", "搜索引擎"],
    "hao123.com": ["搜索与门户", "网址导航"], "2345.com": ["搜索与门户", "网址导航"],
    "qq.com": ["搜索与门户", "综合门户"], "sina.com.cn": ["搜索与门户", "综合门户"],
    "sohu.com": ["搜索与门户", "综合门户"], "163.com": ["搜索与门户", "综合门户"],
    "ifeng.com": ["搜索与门户", "综合门户"], "people.com.cn": ["新闻资讯", "综合新闻"],
    "xinhuanet.com": ["新闻资讯", "综合新闻"], "cctv.com": ["新闻资讯", "综合新闻"],
    "china.com.cn": ["新闻资讯", "综合新闻"], "cnr.cn": ["新闻资讯", "综合新闻"],
    # ==== 新闻资讯 ====
    "toutiao.com": ["新闻资讯", "资讯聚合"], "eastmoney.com": ["金融与理财", "财经资讯"],
    "wallstreetcn.com": ["金融与理财", "财经资讯"], "cls.cn": ["金融与理财", "财经资讯"],
    "jin10.com": ["金融与理财", "财经资讯"], "bloomberg.com": ["金融与理财", "财经资讯"],
    "reuters.com": ["金融与理财", "财经资讯"], "ft.com": ["金融与理财", "财经资讯"],
    "cnbc.com": ["金融与理财", "财经资讯"], "hupu.com": ["新闻资讯", "体育"],
    "dongqiudi.com": ["新闻资讯", "体育"], "espn.com": ["新闻资讯", "体育"],
    "zhibo8.cc": ["新闻资讯", "体育"], "36kr.com": ["新闻资讯", "科技资讯"],
    "ithome.com": ["新闻资讯", "科技资讯"], "leiphone.com": ["新闻资讯", "科技资讯"],
    "huxiu.com": ["新闻资讯", "科技资讯"], "pingwest.com": ["新闻资讯", "科技资讯"],
    "cnbeta.com": ["新闻资讯", "科技资讯"], "solidot.org": ["新闻资讯", "科技资讯"],
    # ==== 社交与社区 ====
    "weibo.com": ["社交与社区", "微博与社交"], "zhihu.com": ["社交与社区", "知识社区"],
    "zhuanlan.zhihu.com": ["社交与社区", "知识社区"], "tieba.baidu.com": ["社交与社区", "贴吧论坛"],
    "douban.com": ["社交与社区", "兴趣社区"], "reddit.com": ["社交与社区", "海外社区"],
    "x.com": ["社交与社区", "海外社交"], "twitter.com": ["社交与社区", "海外社交"],
    "facebook.com": ["社交与社区", "海外社交"], "instagram.com": ["社交与社区", "海外社交"],
    "tiktok.com": ["社交与社区", "海外社交"], "tianya.cn": ["社交与社区", "贴吧论坛"],
    "v2ex.com": ["社交与社区", "技术社区"], "linux.do": ["社交与社区", "技术社区"],
    "nodeseek.com": ["社交与社区", "技术社区"], "hostloc.com": ["社交与社区", "技术社区"],
    "52pojie.cn": ["社交与社区", "技术社区"], "sspai.com": ["社交与社区", "技术社区"],
    "qzone.qq.com": ["社交与社区", "微博与社交"],
    # ==== 视频与直播 ====
    "bilibili.com": ["视频与直播", "在线视频"], "youtube.com": ["视频与直播", "在线视频"],
    "youku.com": ["视频与直播", "在线视频"], "iqiyi.com": ["视频与直播", "在线视频"],
    "mango.tv": ["视频与直播", "在线视频"], "v.qq.com": ["视频与直播", "在线视频"],
    "douyin.com": ["视频与直播", "短视频直播"], "kuaishou.com": ["视频与直播", "短视频直播"],
    "huya.com": ["视频与直播", "短视频直播"], "douyu.com": ["视频与直播", "短视频直播"],
    "xigua.com": ["视频与直播", "短视频直播"], "acfun.cn": ["视频与直播", "在线视频"],
    "twitch.tv": ["视频与直播", "海外直播"], "netflix.com": ["视频与直播", "海外视频"],
    "vimeo.com": ["视频与直播", "海外视频"], "dailymotion.com": ["视频与直播", "海外视频"],
    "tv.sohu.com": ["视频与直播", "在线视频"], "pptv.com": ["视频与直播", "在线视频"],
    # ==== 音乐与音频 ====
    "music.163.com": ["音乐与音频", "在线音乐"], "y.qq.com": ["音乐与音频", "在线音乐"],
    "kugou.com": ["音乐与音频", "在线音乐"], "kuwo.cn": ["音乐与音频", "在线音乐"],
    "ximalaya.com": ["音乐与音频", "有声电台"], "lizhi.fm": ["音乐与音频", "有声电台"],
    "qingting.fm": ["音乐与音频", "有声电台"], "spotify.com": ["音乐与音频", "海外音乐"],
    "soundcloud.com": ["音乐与音频", "海外音乐"], "bandcamp.com": ["音乐与音频", "海外音乐"],
    # ==== 游戏与电竞 ====
    "steampowered.com": ["游戏与电竞", "游戏平台"], "store.steampowered.com": ["游戏与电竞", "游戏平台"],
    "epicgames.com": ["游戏与电竞", "游戏平台"], "gog.com": ["游戏与电竞", "游戏平台"],
    "xbox.com": ["游戏与电竞", "游戏平台"], "playstation.com": ["游戏与电竞", "游戏平台"],
    "nintendo.com": ["游戏与电竞", "游戏平台"], "wegame.com": ["游戏与电竞", "游戏平台"],
    "taptap.cn": ["游戏与电竞", "游戏平台"], "4399.com": ["游戏与电竞", "游戏平台"],
    "17173.com": ["游戏与电竞", "游戏资讯"], "gamersky.com": ["游戏与电竞", "游戏资讯"],
    "ign.com": ["游戏与电竞", "游戏资讯"], "battle.net": ["游戏与电竞", "游戏平台"],
    "riotgames.com": ["游戏与电竞", "游戏平台"], "minecraft.net": ["游戏与电竞", "Minecraft"],
    "mcmod.cn": ["游戏与电竞", "Minecraft"], "modrinth.com": ["游戏与电竞", "Minecraft"],
    "curseforge.com": ["游戏与电竞", "Minecraft"], "minebbs.com": ["游戏与电竞", "Minecraft"],
    "nexusmods.com": ["游戏与电竞", "游戏MOD"], "3dmgame.com": ["游戏与电竞", "游戏下载"],
    "gamer520.com": ["游戏与电竞", "游戏下载"], "game777.cn": ["游戏与电竞", "游戏下载"],
    "onlinefix618.com": ["游戏与电竞", "游戏补丁"], "steamdb.info": ["游戏与电竞", "游戏工具"],
    # ==== 购物与电商 ====
    "taobao.com": ["购物与电商", "综合电商"], "tmall.com": ["购物与电商", "综合电商"],
    "jd.com": ["购物与电商", "综合电商"], "pinduoduo.com": ["购物与电商", "综合电商"],
    "suning.com": ["购物与电商", "综合电商"], "gome.com.cn": ["购物与电商", "综合电商"],
    "dangdang.com": ["购物与电商", "图书电商"], "amazon.com": ["购物与电商", "海外电商"],
    "amazon.cn": ["购物与电商", "海外电商"], "ebay.com": ["购物与电商", "海外电商"],
    "aliexpress.com": ["购物与电商", "海外电商"], "alibaba.com": ["购物与电商", "B2B电商"],
    "1688.com": ["购物与电商", "B2B电商"], "vip.com": ["购物与电商", "综合电商"],
    "goofish.com": ["购物与电商", "二手交易"], "dewu.com": ["购物与电商", "潮流电商"],
    "smzdm.com": ["购物与电商", "购物指南"], "kaola.com": ["购物与电商", "综合电商"],
    "xiaohongshu.com": ["社交与社区", "兴趣社区"], "xianyu": ["购物与电商", "二手交易"],
    # ==== 美食与生活 ====
    "xiachufang.com": ["美食与生活", "菜谱美食"], "meishij.net": ["美食与生活", "菜谱美食"],
    "meituan.com": ["美食与生活", "本地生活"], "dianping.com": ["美食与生活", "本地生活"],
    "ele.me": ["美食与生活", "外卖"], "koubei.com": ["美食与生活", "本地生活"],
    "58.com": ["美食与生活", "生活服务"], "ganji.com": ["美食与生活", "生活服务"],
    "baixing.com": ["美食与生活", "生活服务"],
    # ==== 旅游与出行 ====
    "amap.com": ["旅游与出行", "地图导航"], "map.baidu.com": ["旅游与出行", "地图导航"],
    "map.qq.com": ["旅游与出行", "地图导航"], "gaode.com": ["旅游与出行", "地图导航"],
    "qunar.com": ["旅游与出行", "在线旅游"], "ctrip.com": ["旅游与出行", "在线旅游"],
    "mafengwo.cn": ["旅游与出行", "旅游攻略"], "tuniu.com": ["旅游与出行", "在线旅游"],
    "ly.com": ["旅游与出行", "在线旅游"], "airbnb.com": ["旅游与出行", "住宿预订"],
    "booking.com": ["旅游与出行", "住宿预订"], "12306.cn": ["旅游与出行", "交通票务"],
    "fliggy.com": ["旅游与出行", "在线旅游"], "didi.com": ["旅游与出行", "出行服务"],
    "autohome.com.cn": ["旅游与出行", "汽车资讯"], "pcauto.com.cn": ["旅游与出行", "汽车资讯"],
    "xcar.com.cn": ["旅游与出行", "汽车资讯"], "dongchedi.com": ["旅游与出行", "汽车资讯"],
    "bitauto.com": ["旅游与出行", "汽车资讯"], "yiche.com": ["旅游与出行", "汽车资讯"],
    "xiaozhu.com": ["旅游与出行", "住宿预订"],
    # ==== 医疗与健康 ====
    "haodf.com": ["医疗与健康", "在线医疗"], "dxy.cn": ["医疗与健康", "健康科普"],
    "39.net": ["医疗与健康", "健康科普"], "xywy.com": ["医疗与健康", "在线医疗"],
    "fh21.com.cn": ["医疗与健康", "健康科普"], "guahao.com": ["医疗与健康", "在线医疗"],
    "medlive.cn": ["医疗与健康", "在线医疗"], "jianke.com": ["医疗与健康", "在线医疗"],
    "dxy.com": ["医疗与健康", "健康科普"],
    # ==== 教育与学习 ====
    "icourse163.org": ["教育与学习", "在线教育"], "xuetangx.com": ["教育与学习", "在线教育"],
    "study.163.com": ["教育与学习", "在线教育"], "zhihuishu.com": ["教育与学习", "在线教育"],
    "xdf.cn": ["教育与学习", "教育培训"], "hujiang.com": ["教育与学习", "在线教育"],
    "duolingo.com": ["教育与学习", "外语学习"], "coursera.org": ["教育与学习", "在线教育"],
    "edx.org": ["教育与学习", "在线教育"], "khanacademy.org": ["教育与学习", "在线教育"],
    "udemy.com": ["教育与学习", "在线教育"], "geekbang.org": ["教育与学习", "IT培训"],
    "chsi.com.cn": ["教育与学习", "学籍学历"], "gaokao.com": ["教育与学习", "升学考试"],
    "examcoo.com": ["教育与学习", "考试平台"], "kkdaxue.com": ["教育与学习", "教育导航"],
    "afuketang.com": ["教育与学习", "考试平台"], "cnki.net": ["阅读与知识", "学术文献"],
    "wanfangdata.com.cn": ["阅读与知识", "学术文献"], "cqvip.com": ["阅读与知识", "学术文献"],
    # ==== 金融与理财 ====
    "alipay.com": ["金融与理财", "支付工具"], "paypal.com": ["金融与理财", "支付工具"],
    "icbc.com.cn": ["金融与理财", "银行"], "ccb.com": ["金融与理财", "银行"],
    "boc.cn": ["金融与理财", "银行"], "abchina.com": ["金融与理财", "银行"],
    "cmbchina.com": ["金融与理财", "银行"], "boc.com": ["金融与理财", "银行"],
    "10jqka.com.cn": ["金融与理财", "股票基金"], "danjuanfunds.com": ["金融与理财", "股票基金"],
    "xueqiu.com": ["金融与理财", "股票基金"], "binance.com": ["金融与理财", "加密货币"],
    "okx.com": ["金融与理财", "加密货币"], "huobi.com": ["金融与理财", "加密货币"],
    "coinbase.com": ["金融与理财", "加密货币"], "ethereum.org": ["金融与理财", "加密货币"],
    # ==== 办公与协作 ====
    "office.com": ["办公与协作", "办公套件"], "wps.cn": ["办公与协作", "办公套件"],
    "feishu.cn": ["办公与协作", "协作平台"], "larksuite.com": ["办公与协作", "协作平台"],
    "dingtalk.com": ["办公与协作", "协作平台"], "docs.qq.com": ["办公与协作", "在线文档"],
    "docs.wps.cn": ["办公与协作", "在线文档"], "kdocs.cn": ["办公与协作", "在线文档"],
    "yuque.com": ["办公与协作", "在线文档"], "notion.so": ["办公与协作", "在线文档"],
    "shimo.im": ["办公与协作", "在线文档"], "meeting.tencent.com": ["办公与协作", "视频会议"],
    "zoom.us": ["办公与协作", "视频会议"], "gmail.com": ["办公与协作", "邮箱"],
    "mail.qq.com": ["办公与协作", "邮箱"], "mail.163.com": ["办公与协作", "邮箱"],
    "126.com": ["办公与协作", "邮箱"], "outlook.com": ["办公与协作", "邮箱"],
    "officeplus.cn": ["办公与协作", "PPT与模板"],
    # ==== 开发与编程 ====
    "github.com": ["开发与编程", "代码托管"], "gitlab.com": ["开发与编程", "代码托管"],
    "bitbucket.org": ["开发与编程", "代码托管"], "gitee.com": ["开发与编程", "代码托管"],
    "gitcode.com": ["开发与编程", "代码托管"], "csdn.net": ["开发与编程", "技术社区"],
    "blog.csdn.net": ["开发与编程", "技术社区"], "cnblogs.com": ["开发与编程", "技术社区"],
    "juejin.cn": ["开发与编程", "技术社区"], "segmentfault.com": ["开发与编程", "技术社区"],
    "stackoverflow.com": ["开发与编程", "海外问答"], "leetcode.cn": ["开发与编程", "刷题面试"],
    "nowcoder.com": ["开发与编程", "刷题面试"], "jb51.net": ["开发与编程", "脚本之家"],
    "runoob.com": ["开发与编程", "教程文档"], "w3school.com.cn": ["开发与编程", "教程文档"],
    "developer.mozilla.org": ["开发与编程", "教程文档"], "python.org": ["开发与编程", "编程语言"],
    "nodejs.org": ["开发与编程", "编程语言"], "docker.com": ["开发与编程", "开发工具"],
    "npmjs.com": ["开发与编程", "开发工具"], "pypi.org": ["开发与编程", "开发工具"],
    "jetbrains.com": ["开发与编程", "开发工具"], "visualstudio.com": ["开发与编程", "开发工具"],
    "aliyun.com": ["开发与编程", "云服务"], "cloud.tencent.com": ["开发与编程", "云服务"],
    "huaweicloud.com": ["开发与编程", "云服务"], "qiniu.com": ["开发与编程", "云服务"],
    "cloudflare.com": ["开发与编程", "云服务"], "vercel.com": ["开发与编程", "云服务"],
    "aws.amazon.com": ["开发与编程", "云服务"], "azure.microsoft.com": ["开发与编程", "云服务"],
    "cloud.google.com": ["开发与编程", "云服务"], "bgithub.xyz": ["开发与编程", "代码托管"],
    "kkgithub.com": ["开发与编程", "代码托管"], "gh-proxy.com": ["开发与编程", "代码托管"],
    # ==== AI 人工智能 ====
    "openai.com": ["AI 人工智能", "对话与助手"], "chat.openai.com": ["AI 人工智能", "对话与助手"],
    "anthropic.com": ["AI 人工智能", "对话与助手"], "claude.ai": ["AI 人工智能", "对话与助手"],
    "deepseek.com": ["AI 人工智能", "对话与助手"], "chat.deepseek.com": ["AI 人工智能", "对话与助手"],
    "qianwenai.com": ["AI 人工智能", "对话与助手"], "tongyi.com": ["AI 人工智能", "对话与助手"],
    "moonshot.cn": ["AI 人工智能", "对话与助手"], "kimi.com": ["AI 人工智能", "对话与助手"],
    "zhipuai.cn": ["AI 人工智能", "对话与助手"], "yiyan.baidu.com": ["AI 人工智能", "对话与助手"],
    "xfyun.cn": ["AI 人工智能", "对话与助手"], "doubao.com": ["AI 人工智能", "对话与助手"],
    "yuanbao.tencent.com": ["AI 人工智能", "对话与助手"], "minimaxi.com": ["AI 人工智能", "语音与音乐"],
    "minnimax.chat": ["AI 人工智能", "API与平台"], "jimeng.jianying.com": ["AI 人工智能", "图像生成"],
    "civitai.com": ["AI 人工智能", "图像生成"], "midjourney.com": ["AI 人工智能", "图像生成"],
    "stable-diffusion": ["AI 人工智能", "图像生成"], "huggingface.co": ["AI 人工智能", "模型社区"],
    "sora.com": ["AI 人工智能", "视频生成"], "runwayml.com": ["AI 人工智能", "视频生成"],
    "vidu.studio": ["AI 人工智能", "视频生成"], "openrouter.ai": ["AI 人工智能", "API与平台"],
    "siliconflow.cn": ["AI 人工智能", "API与平台"], "cloud.siliconflow.cn": ["AI 人工智能", "API与平台"],
    "elevenlabs.io": ["AI 人工智能", "语音与音乐"], "suno.com": ["AI 人工智能", "语音与音乐"],
    "fish.audio": ["AI 人工智能", "语音与音乐"], "ttsmaker.cn": ["AI 人工智能", "语音与音乐"],
    "perplexity.ai": ["AI 人工智能", "对话与助手"], "gemini.google.com": ["AI 人工智能", "对话与助手"],
    "notebooklm.google": ["AI 人工智能", "对话与助手"], "modelscope.cn": ["AI 人工智能", "模型社区"],
    "moge.ai": ["AI 人工智能", "AI导航"], "ai138.com": ["AI 人工智能", "AI导航"],
    "aishenqi.net": ["AI 人工智能", "AI导航"],
    # ==== 设计与创意 ====
    "canva.cn": ["设计与创意", "在线设计"], "canva.com": ["设计与创意", "在线设计"],
    "figma.com": ["设计与创意", "在线设计"], "adobe.com": ["设计与创意", "设计软件"],
    "zcool.com.cn": ["设计与创意", "设计社区"], "huaban.com": ["设计与创意", "灵感采集"],
    "behance.net": ["设计与创意", "灵感采集"], "dribbble.com": ["设计与创意", "灵感采集"],
    "unsplash.com": ["设计与创意", "图库素材"], "pexels.com": ["设计与创意", "图库素材"],
    "pixabay.com": ["设计与创意", "图库素材"], "58pic.com": ["设计与创意", "图库素材"],
    "588ku.com": ["设计与创意", "图库素材"], "nipic.com": ["设计与创意", "图库素材"],
    "aigei.com": ["设计与创意", "素材资源"], "coolors.co": ["设计与创意", "配色工具"],
    "color.adobe.com": ["设计与创意", "配色工具"], "free3d.com": ["设计与创意", "3D模型"],
    "cgtrader.com": ["设计与创意", "3D模型"], "turbosquid.com": ["设计与创意", "3D模型"],
    "sketchfab.com": ["设计与创意", "3D模型"], "blender.org": ["设计与创意", "设计软件"],
    "zitiwang.com": ["设计与创意", "字体资源"], "gaituya.com": ["设计与创意", "图片处理"],
    "photopea.com": ["设计与创意", "在线设计"], "ps.gaoding.com": ["设计与创意", "在线设计"],
    "aiyijian.com": ["设计与创意", "素材资源"],
    # ==== 工具与效率 ====
    "convertio.co": ["工具与效率", "在线转换"], "ilovepdf.com": ["工具与效率", "在线转换"],
    "tools.pdf24.org": ["工具与效率", "在线转换"], "smallpdf.com": ["工具与效率", "在线转换"],
    "pdfcandy.com": ["工具与效率", "在线转换"], "tinypng.com": ["工具与效率", "图片压缩"],
    "deepl.com": ["工具与效率", "翻译工具"], "fanyi.baidu.com": ["工具与效率", "翻译工具"],
    "translate.google.com": ["工具与效率", "翻译工具"], "youdao.com": ["工具与效率", "翻译工具"],
    "iciba.com": ["工具与效率", "词典工具"], "weather.com.cn": ["工具与效率", "天气查询"],
    "qweather.com": ["工具与效率", "天气查询"], "ghxi.com": ["工具与效率", "软件下载"],
    "zol.com.cn": ["工具与效率", "软件下载"], "ruancang.net": ["工具与效率", "软件下载"],
    "dismplus.com": ["工具与效率", "系统工具"], "todesk.com": ["工具与效率", "远程控制"],
    "sunlogin.com": ["工具与效率", "远程控制"], "anydesk.com": ["工具与效率", "远程控制"],
    "teamviewer.com": ["工具与效率", "远程控制"], "parsec.app": ["工具与效率", "远程控制"],
    "zerotier.com": ["工具与效率", "网络工具"], "tailscale.com": ["工具与效率", "网络工具"],
    "frpee.com": ["工具与效率", "网络工具"], "natfrp.com": ["工具与效率", "网络工具"],
    "virustotal.com": ["工具与效率", "安全检测"], "virscan.org": ["工具与效率", "安全检测"],
    "habo.qq.com": ["工具与效率", "安全检测"], "linshi-email.com": ["工具与效率", "临时邮箱"],
    "tenminutesmail.net": ["工具与效率", "临时邮箱"], "urlc.cn": ["工具与效率", "短链接"],
    "otp.landian.vip": ["工具与效率", "系统工具"], "crxsoso.com": ["工具与效率", "浏览器扩展"],
    "chromewu.com": ["工具与效率", "浏览器扩展"], "pixpinapp.com": ["工具与效率", "截图工具"],
    "jyshare.com": ["工具与效率", "编码工具"],
    # ==== 网盘与存储 ====
    "pan.baidu.com": ["网盘与存储", "百度网盘"], "pan.quark.cn": ["网盘与存储", "夸克网盘"],
    "lanzoue.com": ["网盘与存储", "蓝奏云"], "lanzouj.com": ["网盘与存储", "蓝奏云"],
    "lanzoux.com": ["网盘与存储", "蓝奏云"], "lanzn.com": ["网盘与存储", "蓝奏云"],
    "aliyundrive.com": ["网盘与存储", "阿里云盘"], "alipan.com": ["网盘与存储", "阿里云盘"],
    "123pan.com": ["网盘与存储", "123云盘"], "115.com": ["网盘与存储", "115网盘"],
    "pan.xunlei.com": ["网盘与存储", "迅雷云盘"], "cloud.189.cn": ["网盘与存储", "天翼云盘"],
    "cowtransfer.com": ["网盘与存储", "文件传输"], "wormhole.app": ["网盘与存储", "文件传输"],
    "wetransfer.com": ["网盘与存储", "文件传输"], "mega.nz": ["网盘与存储", "海外网盘"],
    "weiyun.com": ["网盘与存储", "微云"], "quarkpanso.com": ["网盘与存储", "网盘搜索"],
    "chaonengso.com": ["网盘与存储", "网盘搜索"], "yunso.net": ["网盘与存储", "网盘搜索"],
    "kkpans.com": ["网盘与存储", "网盘搜索"], "yp.laosu.xyz": ["网盘与存储", "网盘搜索"],
    "kuafuzy.com": ["网盘与存储", "资源分享"], "kuafuzy.cc": ["网盘与存储", "资源分享"],
    # ==== 阅读与知识 ====
    "baike.baidu.com": ["阅读与知识", "百科知识"], "wikipedia.org": ["阅读与知识", "百科知识"],
    "zh.wikipedia.org": ["阅读与知识", "百科知识"], "qidian.com": ["阅读与知识", "网络文学"],
    "zongheng.com": ["阅读与知识", "网络文学"], "weread.qq.com": ["阅读与知识", "电子书"],
    "go-to-library.sk": ["阅读与知识", "电子书库"], "annas-archive.org": ["阅读与知识", "电子书库"],
    "pdfdrive.com": ["阅读与知识", "电子书库"], "jiumodiary.com": ["阅读与知识", "文档搜索"],
    "24hbook.store": ["阅读与知识", "电子书库"], "scholar.google.com": ["阅读与知识", "学术文献"],
    "bqg107.xyz": ["阅读与知识", "网络文学"], "blog.hgtrojan.com": ["阅读与知识", "网络文学"],
    # ==== 壁纸与美化 ====
    "wallhaven.cc": ["壁纸与美化", "壁纸网站"], "wallhere.com": ["壁纸与美化", "壁纸网站"],
    "bz.zzzmh.cn": ["壁纸与美化", "壁纸网站"], "pic.netbian.com": ["壁纸与美化", "壁纸网站"],
    "haowallpaper.com": ["壁纸与美化", "壁纸网站"], "uhdpaper.com": ["壁纸与美化", "壁纸网站"],
    "iphoneswallpapers.com": ["壁纸与美化", "壁纸网站"], "4kwallpapers.com": ["壁纸与美化", "壁纸网站"],
    "bizhihui.com": ["壁纸与美化", "壁纸网站"], "upupoo.com": ["壁纸与美化", "桌面美化"],
    "zhutix.com": ["壁纸与美化", "桌面美化"], "rainmeter.net": ["壁纸与美化", "桌面美化"],
    "bitdock.cn": ["壁纸与美化", "桌面美化"], "sapphire.icu": ["壁纸与美化", "桌面美化"],
    "go.itab.link": ["壁纸与美化", "桌面美化"], "aizhinan.github.io": ["壁纸与美化", "桌面美化"],
    # ==== 政府与公共 ====
    "gov.cn": ["政府与公共", "政务服务"], "12315.cn": ["政府与公共", "政务服务"],
    "12333.gov.cn": ["政府与公共", "社会保障"], "12123.gov.cn": ["政府与公共", "交通管理"],
    "chinatax.gov.cn": ["政府与公共", "税务服务"], "miit.gov.cn": ["政府与公共", "政务服务"],
    # ==== 其他通用 ====
    "koyso.com": ["工具与效率", "效率工具"], "fuun.fun": ["工具与效率", "效率工具"],
    "youxiaohou.com": ["工具与效率", "效率工具"], "4275.com": ["网盘与存储", "文件传输"],
    "yemao.in": ["工具与效率", "资源导航"], "flysheep6.com": ["工具与效率", "资源导航"],
    "ghxi.com": ["工具与效率", "软件下载"],
}

# ---------------- 旧规则迁移映射（旧大类 -> 新大类） ----------------
OLD_TO_NEW = {
    "Minecraft": "游戏与电竞", "AI": "AI 人工智能", "游戏娱乐": "游戏与电竞",
    "开发开源": "开发与编程", "实用工具": "工具与效率", "办公学习": "办公与协作",
    "设计创作": "设计与创意", "影音阅读": "视频与直播", "壁纸美化": "壁纸与美化",
    "其他": "其他",
}
# 旧(大类,二级) -> 新(大类,二级) 特殊调整
SUB_ADJUST = {
    ("实用工具", "网盘与文件共享"): ("网盘与存储", "网盘与文件共享"),
    ("办公学习", "学习教育"): ("教育与学习", "学习教育"),
    ("办公学习", "PPT与模板"): ("办公与协作", "PPT与模板"),
    ("办公学习", "文档与办公"): ("办公与协作", "文档与办公"),
    ("办公学习", "效率工具"): ("办公与协作", "效率工具"),
    ("影音阅读", "在线影视"): ("视频与直播", "在线影视"),
    ("影音阅读", "影视与音乐下载"): ("视频与直播", "影视与音乐下载"),
    ("影音阅读", "小说阅读"): ("阅读与知识", "小说阅读"),
    ("影音阅读", "电子书与文档库"): ("阅读与知识", "电子书与文档库"),
    ("设计创作", "音频与音乐"): ("音乐与音频", "音乐工具"),
    ("设计创作", "视频剪辑"): ("设计与创意", "视频剪辑"),
    ("设计创作", "3D建模与素材"): ("设计与创意", "3D模型"),
    ("设计创作", "素材与资源"): ("设计与创意", "素材资源"),
    ("设计创作", "配色与字体"): ("设计与创意", "配色工具"),
    ("设计创作", "图片设计"): ("设计与创意", "图片设计"),
    ("设计创作", "在线转换"): ("工具与效率", "在线转换"),
    ("实用工具", "在线转换与处理"): ("工具与效率", "在线转换"),
    ("实用工具", "效率小工具"): ("工具与效率", "效率小工具"),
    ("实用工具", "远程控制与串流"): ("工具与效率", "远程控制"),
    ("实用工具", "网络与代理"): ("工具与效率", "网络工具"),
    ("实用工具", "下载与解析"): ("工具与效率", "下载与解析"),
    ("实用工具", "系统与软件"): ("工具与效率", "系统工具"),
    ("实用工具", "安全与检测"): ("工具与效率", "安全检测"),
}


def convert(cat, sub):
    if (cat, sub) in SUB_ADJUST:
        return SUB_ADJUST[(cat, sub)]
    return (OLD_TO_NEW.get(cat, cat), sub)


def main():
    # 1) 读取旧规则
    sys.path.insert(0, ".")
    import classify as C
    import inspect
    src = inspect.getsource(C)

    def extract(name):
        m = re.search(rf'{name} = \[(.*?)\n\]', src, re.S)
        if not m:
            return []
        block = m.group(1)
        return [(p, c, s) for p, c, s in re.findall(r'\(r"(.*?)", \("(.*?)", "(.*?)"\)\)', block)]

    old_dom_map = {k: convert(*v) for k, v in C.DOMAIN_MAP.items()}
    old_sub = {
        "github.com": [(p, *convert(c, s)) for p, c, s in extract("GITHUB_RULES")],
        "afdian.com": [(p, *convert(c, s)) for p, c, s in extract("AFDIAN_RULES")],
        "zhuanlan.zhihu.com": [(p, *convert(c, s)) for p, c, s in extract("ZHIHU_RULES")],
        "blog.csdn.net": [(p, *convert(c, s)) for p, c, s in extract("CSDN_RULES")],
        "bilibili.com": [(p, *convert(c, s)) for p, c, s in extract("BILIBILI_RULES")],
    }
    old_fb = [(p, *convert(c, s)) for p, c, s in extract("FALLBACK_RULES")]

    # 2) 合并域名映射（旧规则 + 通用扩展，通用覆盖）
    dom_map = {}
    for k, v in old_dom_map.items():
        if k not in GENERIC:
            dom_map[k] = v
    dom_map.update(GENERIC)

    # 3) 合并子规则（旧 + 通用扩展的 zhihu/github/bilibili 等已含在 GENERIC 域名映射，
    #    子规则保留旧的用于标题细分；zhihu.com 域名本身在 GENERIC 映射，但子规则在
    #    zhuanlan.zhihu.com 下。补充 zhihu.com/csdn.net 别名子规则）
    sub_rules = dict(old_sub)
    # 通用子规则：内容混杂域名按标题细分（大类已通用化）
    sub_rules.setdefault("zhihu.com", sub_rules.get("zhuanlan.zhihu.com", []))
    sub_rules.setdefault("csdn.net", sub_rules.get("blog.csdn.net", []))

    # 4) 合并兜底（旧 + 通用补充，顺序: 旧在前）
    generic_fb = [
        (r"菜谱|美食|下厨房|做饭|食谱|烘焙", ["美食与生活", "菜谱美食"]),
        (r"健身|运动|keep|瑜伽|跑步|减肥", ["医疗与健康", "健身运动"]),
        (r"汽车|买车|4s|车型|汽车之家", ["旅游与出行", "汽车资讯"]),
        (r"新闻|资讯|时报|日报|快讯|头条", ["新闻资讯", "综合新闻"]),
        (r"股票|基金|理财|银行|支付|比特币|区块链|加密货币", ["金融与理财", "股票基金"]),
        (r"购物|商城|买|秒杀|优惠券|正品", ["购物与电商", "综合电商"]),
        (r"机票|酒店|旅游|攻略|签证|火车票|民宿", ["旅游与出行", "在线旅游"]),
        (r"医院|医生|挂号|药品|健康|养生|疾病", ["医疗与健康", "在线医疗"]),
        (r"招聘|求职|简历|猎头|职场", ["办公与协作", "招聘求职"]),
        (r"地图|导航|公交|路线", ["旅游与出行", "地图导航"]),
        (r"天气|气温|预报", ["工具与效率", "天气查询"]),
        (r"字典|词典|翻译|英语|外语", ["教育与学习", "外语学习"]),
        (r"菜鸟|教程|学习|课程|mooc|慕课|公开课", ["教育与学习", "在线教育"]),
        (r"政务|办事|社保|公积金|税务|政府", ["政府与公共", "政务服务"]),
    ]
    fb = []
    for p, c, s in old_fb:
        fb.append([p, c, s])
    for p, (c, s) in generic_fb:
        fb.append([p, c, s])

    # 5) 网盘豁免域名
    netdisk = sorted({
        "pan.baidu.com", "pan.quark.cn", "lanzoue.com", "lanzouj.com", "lanzoux.com",
        "lanzn.com", "aliyundrive.com", "alipan.com", "123pan.com", "115.com",
        "pan.xunlei.com", "cloud.189.cn", "cowtransfer.com", "wormhole.app",
        "pan.xfyzyyb.xyz", "yun.139.com", "weiyun.com", "wetransfer.com", "mega.nz",
    })

    rules = {
        "大类顺序": CATS,
        "域名映射": dict(sorted(dom_map.items(), key=lambda x: x[0])),
        "子规则": {k: [list(x) for x in v] for k, v in sub_rules.items() if v},
        "兜底关键词": fb,
        "网盘域名": netdisk,
    }

    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=1)

    print("通用 categories.json 已生成")
    print("大类:", len(CATS), "个 ->", " / ".join(CATS[:6]) + " ...")
    print("域名映射:", len(dom_map), "条")
    print("子规则:", {k: len(v) for k, v in sub_rules.items() if v})
    print("兜底关键词:", len(fb), "条")
    print("网盘域名:", len(netdisk), "个")


if __name__ == "__main__":
    main()
