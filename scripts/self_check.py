# -*- coding: utf-8 -*-
"""Minimal self-check: domain suffix matching + rules load. Exit 1 on failure."""
import os
import sys

from organizer import Classifier, domain_candidates, load_rules

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
RULES = os.path.join(SKILL_ROOT, "categories.json")


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
    assert rules.get("域名映射"), "categories.json missing 域名映射"
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
