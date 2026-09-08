# -*- coding: utf-8 -*-
"""最小自检：后缀匹配 + 规则加载。失败即 exit 1。"""
import os
import sys

from organizer import Classifier, domain_candidates, load_rules

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "categories.json")


def test_domain_candidates():
    assert domain_candidates("author.baidu.com") == [
        "author.baidu.com", "baidu.com"
    ]
    assert domain_candidates("dash.cloudflare.com") == [
        "dash.cloudflare.com", "cloudflare.com"
    ]
    assert domain_candidates("124.220.104.35:9000") == ["124.220.104.35:9000"]


def test_load_and_classify():
    rules = load_rules(RULES)
    assert rules.get("域名映射"), "categories.json 缺少域名映射"
    clf = Classifier(rules)
    c, s, how = clf.classify("GitHub", "https://github.com/demo/repo")
    assert c and how == "域名映射", (c, s, how)


def main():
    test_domain_candidates()
    test_load_and_classify()
    print("self_check OK")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)
