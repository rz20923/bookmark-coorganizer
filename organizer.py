# -*- coding: utf-8 -*-
"""
收藏夹整理通用引擎 (bookmark-organizer)
======================================
适用于任意 Edge/Chrome 收藏夹导出 HTML（Netscape Bookmark 格式）。
流水线：解析 → 自适应分类 → 失效检测 → 去重 → 三层结构生成 → 报告 → 验证。

用法:
    python organizer.py <收藏夹.html> [--categories categories.json] [--out 前缀]
                     [--mode auto|preserve|scheme] [--preview] [--no-check]

特性:
- 三层结构: 收藏夹栏 → 大类 → 二级分类 → 链接
- --mode auto: 通用规则库；preserve: 原文件夹；scheme: 路径映射+域名（共创方案）
- --preview: 只解析+分类，打印摘要，不写文件、不联网
- 失效检测: 并发 HTTP；403/SSL/5xx 存疑保留；--no-check 跳过
- 去重: 规范化 URL（去 www/尾斜杠/fragment/ref 参数）。
"""
import argparse
import csv
import json
import os
import re
import socket
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs, urlencode

# ============================================================
# 1. 解析 Netscape Bookmark HTML
# ============================================================
class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.root = {"name": "ROOT", "kind": "folder", "children": []}
        self.cur_text = None
        self.cur_attrs = None
        self.in_a = False
        self.in_h3 = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h3":
            self.in_h3 = True; self.cur_text = ""
        elif tag == "a":
            self.in_a = True; self.cur_text = ""; self.cur_attrs = d

    def handle_data(self, data):
        if self.in_a or self.in_h3:
            self.cur_text += data

    def handle_endtag(self, tag):
        if tag == "h3" and self.in_h3:
            parent = self.stack[-1] if self.stack else self.root
            node = {"name": self.cur_text.strip(), "kind": "folder", "children": []}
            parent["children"].append(node)
            self.stack.append(node)
            self.in_h3 = False
        elif tag == "a" and self.in_a:
            parent = self.stack[-1] if self.stack else self.root
            node = {
                "name": self.cur_text.strip(), "kind": "link",
                "url": self.cur_attrs.get("href", ""),
                "add_date": self.cur_attrs.get("add_date", ""),
                "icon": self.cur_attrs.get("icon", ""),
            }
            parent["children"].append(node)
            self.in_a = False
        elif tag == "dl":
            if self.stack:
                self.stack.pop()


def parse_bookmarks(html_path):
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    p = BookmarkParser()
    p.feed(content)

    links = []
    def collect(node, path):
        for c in node["children"]:
            if c["kind"] == "link":
                links.append({
                    "name": c["name"], "url": c["url"],
                    "path": path, "add_date": c["add_date"], "icon": c["icon"],
                })
            else:
                collect(c, (path + "/" + c["name"]) if path else c["name"])
    collect(p.root, "")

    # 提取原始 <DT><A ...> 行（保留 ICON 等属性）
    raw_map = {}
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("<DT><A HREF="):
            m = re.search(r'HREF="([^"]*)"', s)
            if m:
                raw_map.setdefault(m.group(1), s)
    for l in links:
        l["raw"] = raw_map.get(l["url"])
    return links, p.root


# ============================================================
# 2. 分类器（规则库 + 自适应聚类）
# ============================================================
def load_rules(path):
    with open(path, encoding="utf-8") as f:
        r = json.load(f)
    r.setdefault("域名映射", {})
    r.setdefault("子规则", {})
    r.setdefault("兜底关键词", [])
    r.setdefault("大类顺序", [])
    r.setdefault("网盘域名", [])
    r.setdefault("路径映射", {})
    return r


def _is_ip_host(dom):
    host = dom.split(":")[0]
    return bool(re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", host))


def domain_candidates(dom):
    """生成域名候选：精确 → 逐级父域。IP:port 只返回自身。"""
    if not dom or _is_ip_host(dom):
        return [dom] if dom else []
    parts = dom.split(".")
    cands = [dom]
    # a.b.c.com → b.c.com, c.com；保留至少两段（含 com.cn 等在映射里写全）
    for i in range(1, len(parts) - 1):
        cands.append(".".join(parts[i:]))
    return cands


class Classifier:
    def __init__(self, rules):
        self.rules = rules
        self.dom_map = rules["域名映射"]
        self.sub_rules = rules["子规则"]
        self.fallback = [(p, c, s) for p, c, s in rules["兜底关键词"]]
        self.netdisk = set(rules["网盘域名"])

    def netloc(self, url):
        try:
            return urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            return ""

    def _sub_rules_for(self, dom):
        for cand in domain_candidates(dom):
            if cand in self.sub_rules:
                return self.sub_rules[cand]
        return []

    def _dom_map_for(self, dom):
        for cand in domain_candidates(dom):
            if cand in self.dom_map:
                return self.dom_map[cand]
        return None

    def classify(self, name, url):
        text = (name + " " + url).lower()
        dom = self.netloc(url)
        # 1) 关键域名标题子规则（含子域后缀）
        for pat, c, s in self._sub_rules_for(dom):
            if re.search(pat, text):
                return c, s, "子规则"
        # 2) 域名映射（精确 → 父域后缀，如 author.baidu.com → baidu.com）
        hit = self._dom_map_for(dom)
        if hit:
            c, s = hit
            return c, s, "域名映射"
        # 3) 兜底关键词
        for pat, c, s in self.fallback:
            if re.search(pat, text):
                return c, s, "兜底"
        return None, None, "未匹配"


def _domain_label(dom):
    """从域名提取可读主名：autohome.com.cn -> autohome; xiachufang.com -> xiachufang"""
    parts = dom.split(".")
    two_part_tld = {"com.cn", "net.cn", "org.cn", "gov.cn", "edu.cn", "co.uk",
                    "com.hk", "com.tw", "com.au", "co.jp", "com.br", "com.mx", "com.sg"}
    if len(parts) >= 3 and ".".join(parts[-2:]) in two_part_tld:
        parts = parts[:-2]
    elif len(parts) >= 2:
        parts = parts[:-1]
    return parts[0] if parts else dom


def adaptive_cluster(unmatched):
    """自适应聚类：对规则未命中的链接，按域名聚合生成新二级分类。
    返回 {二级分类: [links]}；域名出现 >=2 次作为可读类别，其余归 '未分类'。
    """
    groups = defaultdict(list)
    for l in unmatched:
        try:
            dom = urlparse(l["url"]).netloc.lower().replace("www.", "")
        except Exception:
            dom = "unknown"
        groups[dom].append(l)
    result = {}
    for dom, ls in groups.items():
        if len(ls) >= 2:
            result.setdefault(f"其他-{_domain_label(dom)}", []).extend(ls)
        else:
            result.setdefault("其他-未分类", []).extend(ls)
    return result


# ============================================================
# 3. 失效检测
# ============================================================
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0")
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _is_netdisk(dom, netdisk_domains):
    for cand in domain_candidates(dom):
        if cand in netdisk_domains:
            return True
    return False


def check_links(links, netdisk_domains, max_workers=40):
    import requests
    def netloc(url):
        try:
            return urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            return ""

    def check_one(item):
        url = item["url"]
        if _is_netdisk(netloc(url), netdisk_domains):
            return {**item, "verdict": "KEEP", "check": "网盘类，不检测"}
        if not url.startswith(("http://", "https://")):
            return {**item, "verdict": "KEEP", "check": f"非http协议: {url[:40]}"}
        last = None
        for _ in range(2):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=(6, 8),
                                    allow_redirects=True, stream=True, verify=True)
                resp.close()
                code = resp.status_code
                if code < 400:
                    return {**item, "verdict": "KEEP", "check": f"HTTP {code}"}
                kind = "反爬" if code == 403 else ("失效" if code < 500 else "临时故障")
                verdict = "KEEP" if kind in ("反爬", "临时故障") else "DELETE"
                return {**item, "verdict": verdict, "check": f"HTTP {code}", "why": kind}
            except requests.exceptions.SSLError as e:
                last = "KEEP", f"SSL错误: {str(e)[:50]}"
            except requests.exceptions.ConnectionError as e:
                last = "DELETE", f"连接失败: {str(e)[:50]}"
            except requests.exceptions.Timeout:
                last = "DELETE", "超时(8s)"
            except requests.exceptions.TooManyRedirects:
                last = "KEEP", "重定向过多"
            except Exception as e:
                last = "KEEP", f"{type(e).__name__}"
            time.sleep(0.3)
        return {**item, "verdict": last[0], "check": last[1]}

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(check_one, l) for l in links]
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            results.append(r)
            if (i + 1) % 100 == 0 or i + 1 == len(links):
                print(f"  检测进度 {i+1}/{len(links)}", flush=True)
    return results


# ============================================================
# 4. 去重
# ============================================================
def norm_url(url):
    try:
        u = urlparse(url)
        host = u.netloc.lower().replace("www.", "")
        path = u.path.rstrip("/") if u.path not in ("", "/") else ""
        q = parse_qs(u.query, keep_blank_values=True)
        for k in [x for x in q if x.lower() in ("ref", "source", "from",
                                                "utm_source", "utm_medium", "utm_campaign")]:
            del q[k]
        qs = urlencode(q, doseq=True)
        return f"{u.scheme}://{host}{path}" + (f"?{qs}" if qs else "")
    except Exception:
        return url


def dedupe(links):
    by = defaultdict(list)
    for l in links:
        by[norm_url(l["url"])].append(l)
    keep_ids, dup = set(), []
    for ls in by.values():
        if len(ls) <= 1:
            keep_ids.add(id(ls[0]))
            continue
        ls.sort(key=lambda x: 0 if x["icon"] else 1)
        keep_ids.add(id(ls[0]))
        for d in ls[1:]:
            dup.append((ls[0], d))
    return [l for l in links if id(l) in keep_ids], dup


# ============================================================
# 5. 生成三层结构 HTML
# ============================================================
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def build_html(tree, cat_order, cat_names):
    lines = []
    lines.append("<!DOCTYPE NETSCAPE-Bookmark-file-1>")
    lines.append("<!-- This is an automatically generated file.")
    lines.append("     It will be read and overwritten.")
    lines.append("     DO NOT EDIT! -->")
    lines.append('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">')
    lines.append("<TITLE>Bookmarks</TITLE>")
    lines.append("<H1>Bookmarks</H1>")
    lines.append("<DL><p>")
    lines.append('    <DT><H3 ADD_DATE="1744450514" LAST_MODIFIED="1785902642" PERSONAL_TOOLBAR_FOLDER="true">收藏夹栏</H3>')
    lines.append("    <DL><p>")
    for cat in cat_order:
        if cat not in tree:
            continue
        label = cat_names.get(cat, cat)
        lines.append(f'        <DT><H3 ADD_DATE="1744450514" LAST_MODIFIED="1785902642">{esc(label)}</H3>')
        lines.append("        <DL><p>")
        for sub, ls in sorted(tree[cat].items(), key=lambda x: -len(x[1])):
            lines.append(f'            <DT><H3 ADD_DATE="1744450514" LAST_MODIFIED="1785902642">{esc(sub)}</H3>')
            lines.append("            <DL><p>")
            for l in ls:
                if l.get("raw"):
                    lines.append("                " + l["raw"])
                else:
                    icon = f' ICON="{esc(l["icon"])}"' if l.get("icon") else ""
                    ad = f' ADD_DATE="{l.get("add_date","")}"' if l.get("add_date") else ""
                    lines.append(f'                <DT><A HREF="{esc(l["url"])}"{ad}{icon}>{esc(l["name"])}</A>')
            lines.append("            </DL><p>")
        lines.append("        </DL><p>")
    lines.append("    </DL><p>")
    lines.append("</DL><p>")
    return "\n".join(lines) + "\n"


# ============================================================
# 6. 验证
# ============================================================
def verify_html(html_path, expected_count):
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    assert html.startswith("<!DOCTYPE NETSCAPE-Bookmark-file-1>"), "缺少 DOCTYPE"
    assert html.count("<DL>") == html.count("</DL>"), "DL 标签不配对"
    assert html.count("<DT><H3") == html.count("</H3>"), "H3 标签不配对"
    p = BookmarkParser()
    p.feed(html)
    def count_links(n):
        return sum(1 if c["kind"] == "link" else count_links(c) for c in n["children"])
    total = count_links(p.root)
    assert total == expected_count, f"链接数不符: {total} != {expected_count}"
    print(f"验证通过: 链接数 {total}，标签配对，HTML 可被 Edge 导入")


# ============================================================
# 分类模式
# ============================================================
_TOOLBAR_NAMES = {"收藏夹栏", "书签栏", "bookmarks bar", "bookmarks toolbar", "favorites bar"}


def path_parts(path):
    parts = [p for p in (path or "").split("/") if p]
    if parts and parts[0].lower() in {x.lower() for x in _TOOLBAR_NAMES}:
        parts = parts[1:]
    return parts


def match_path_rule(path, path_map):
    """最长前缀匹配：路径 '世界/视频/tik' 优先命中 '世界/视频' 再 '世界'。"""
    parts = path_parts(path)
    if not parts or not path_map:
        return None
    for i in range(len(parts), 0, -1):
        key = "/".join(parts[:i])
        if key in path_map:
            c, s = path_map[key]
            return c, s, "路径映射"
    return None


def classify_scheme(links, rules):
    """有原路径则路径优先；根目录/无路径命中再用域名规则；最后自适应。"""
    clf = Classifier(rules)
    path_map = rules.get("路径映射") or {}
    unmatched = []
    for l in links:
        parts = path_parts(l.get("path", ""))
        hit = match_path_rule(l.get("path", ""), path_map) if parts else None
        c, s, how = clf.classify(l["name"], l["url"])
        # 白名单域名：覆盖原文件夹（相册/作家/支付/世界杯/闲鱼等）
        dom = clf.netloc(l["url"])
        force_domains = {
            "photo.baidu.com", "fanqienovel.com", "zuojia.baidu.com",
            "lemonsqueezy.com", "app.lemonsqueezy.com", "paddle.com",
            "vendors.paddle.com", "payoneer.com", "login.payoneer.com",
            "airwallex.com", "paypal.com", "stripe.com", "dashboard.stripe.com",
            "alipay.com", "b.alipay.com",
            "wc-2026.com", "api-football.com", "dashboard.api-football.com",
            "kuaiyupro.com", "imgdiet.com",
            "124.220.104.35:9000",
        }
        from_force = False
        for cand in domain_candidates(dom):
            if cand in force_domains and c:
                l["cat"], l["sub"], l["how"] = c, s, how + "(例外)"
                from_force = True
                break
        if from_force:
            continue
        if hit:
            l["cat"], l["sub"], l["how"] = hit
            continue
        if c:
            l["cat"], l["sub"], l["how"] = c, s, how
            continue
        unmatched.append(l)
    if unmatched:
        print(f"  规则未命中 {len(unmatched)} 条，自适应聚类中 ...")
        for label, ls in adaptive_cluster(unmatched).items():
            sub = label.split("-", 1)[1] if label.startswith("其他") else label
            for l in ls:
                # 根目录散落
                if not path_parts(l.get("path", "")):
                    l["cat"], l["sub"], l["how"] = "根目录", "未整理", "自适应"
                else:
                    l["cat"], l["sub"], l["how"] = "未分类", sub, "自适应"
    return clf


def classify_preserve(links):
    """用原文件夹路径：第一层=大类，其余拼成二级；根链接→未分类。"""
    for l in links:
        parts = path_parts(l.get("path", ""))
        if not parts:
            l["cat"], l["sub"], l["how"] = "未分类", "根目录", "保留原结构"
        elif len(parts) == 1:
            l["cat"], l["sub"], l["how"] = parts[0], "未分组", "保留原结构"
        else:
            l["cat"], l["sub"], l["how"] = parts[0], "/".join(parts[1:]), "保留原结构"


def classify_auto(links, rules):
    clf = Classifier(rules)
    unmatched = []
    for l in links:
        c, s, how = clf.classify(l["name"], l["url"])
        if c:
            l["cat"], l["sub"], l["how"] = c, s, how
        else:
            unmatched.append(l)
    if unmatched:
        print(f"  规则未命中 {len(unmatched)} 条，自适应聚类中 ...")
        for dom, ls in adaptive_cluster(unmatched).items():
            if dom.startswith("其他"):
                cat, sub = "其他", dom.split("-", 1)[1]
            else:
                cat, sub = dom, "自动发现"
            for l in ls:
                l["cat"], l["sub"], l["how"] = cat, sub, "自适应"
    return clf


def print_preview(links, cat_order, samples_per_cat=3):
    print("\n======== 预览（未写文件、未做失效检测）========")
    print(f"共 {len(links)} 条")
    counts = Counter(l["cat"] for l in links)
    for cat in cat_order:
        if cat not in counts:
            continue
        print(f"\n## {cat}（{counts[cat]}）")
        by_sub = defaultdict(list)
        for l in links:
            if l["cat"] == cat:
                by_sub[l["sub"]].append(l)
        for sub, ls in sorted(by_sub.items(), key=lambda x: -len(x[1]))[:8]:
            print(f"  - {sub}: {len(ls)}")
            for l in ls[:samples_per_cat]:
                print(f"      · {l['name'][:60]}")
    leftover = sorted(set(counts) - set(cat_order))
    for cat in leftover:
        print(f"\n## {cat}（{counts[cat]}）")
    print("\n======== 若认可，去掉 --preview 正式运行 ========")


# ============================================================
# 主流程
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="收藏夹整理通用引擎")
    ap.add_argument("input", help="收藏夹 HTML 文件路径")
    ap.add_argument("--categories", default="categories.json", help="分类规则库 JSON")
    ap.add_argument("--out", default="", help="输出文件名前缀（默认取输入文件名的 整理后）")
    ap.add_argument("--no-check", action="store_true", help="跳过失效检测")
    ap.add_argument("--mode", choices=("auto", "preserve", "scheme"), default="auto",
                    help="auto=规则库；preserve=原文件夹；scheme=路径映射+规则（自定义方案）")
    ap.add_argument("--preview", action="store_true",
                    help="只预览分类摘要，不写文件、不联网")
    args = ap.parse_args()

    base = os.path.splitext(os.path.basename(args.input))[0]
    prefix = args.out or (base + "_整理后")
    print(f"[1/6] 解析 {args.input} ...")
    links, _ = parse_bookmarks(args.input)
    print(f"  共 {len(links)} 条链接")

    print(f"[2/6] 分类中（mode={args.mode}）...")
    rules = load_rules(args.categories)
    clf = Classifier(rules)
    if args.mode == "preserve":
        classify_preserve(links)
        cat_order = sorted({l["cat"] for l in links}, key=lambda c: (-sum(1 for l in links if l["cat"] == c), c))
    elif args.mode == "scheme":
        clf = classify_scheme(links, rules)
        cat_order = list(rules["大类顺序"]) + sorted(
            {l["cat"] for l in links} - set(rules["大类顺序"]))
    else:
        clf = classify_auto(links, rules)
        cat_order = list(rules["大类顺序"]) + sorted(
            {l["cat"] for l in links} - set(rules["大类顺序"]))
    print("  分类完成:", dict(Counter(l["cat"] for l in links)))

    if args.preview:
        print_preview(links, cat_order)
        return

    if not args.no_check:
        print("[3/6] 失效检测（并发 HTTP）...")
        links = check_links(links, clf.netdisk)
    else:
        for l in links:
            l["verdict"], l["check"] = "KEEP", "跳过检测"

    dead = [l for l in links if l["verdict"] == "DELETE"]
    keep = [l for l in links if l["verdict"] == "KEEP"]
    doubt = [l for l in keep if l["check"].startswith(("HTTP 4", "HTTP 5", "超时", "连接", "SSL", "DNS"))]
    print(f"  确定失效 {len(dead)} 条，存疑保留 {len(doubt)} 条")

    print("[4/6] 去重 ...")
    keep, dups = dedupe(keep)
    print(f"  删除重复 {len(dups)} 条，剩余 {len(keep)} 条")

    print("[5/6] 生成输出 ...")
    tree = defaultdict(lambda: defaultdict(list))
    for l in keep:
        tree[l["cat"]][l["sub"]].append(l)
    html = build_html(tree, cat_order, {})
    out_html = prefix + ".html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    # 清单
    def wcsv(path, rows):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerows(rows)
    wcsv(prefix + "_失效清单.csv", [["名称", "URL", "检测原因", "归类"]]
         + [[l["name"], l["url"], l["check"], f"{l['cat']}/{l['sub']}"] for l in dead])
    wcsv(prefix + "_存疑清单.csv", [["名称", "URL", "检测原因", "归类"]]
         + [[l["name"], l["url"], l["check"], f"{l['cat']}/{l['sub']}"] for l in doubt])
    wcsv(prefix + "_重复清单.csv", [["保留URL", "删除URL", "删除名称"]]
         + [[d[0]["url"], d[1]["url"], d[1]["name"]] for d in dups])

    # 报告
    rep = [f"# 收藏夹整理报告\n",
           f"- 输入: `{args.input}`（{len(links)} 条）",
           f"- 输出: `{out_html}`（{len(keep)} 条）",
           f"- 删除失效 {len(dead)} 条，删除重复 {len(dups)} 条，存疑保留 {len(doubt)} 条\n",
           "## 分类结构\n", "| 大类 | 链接数 |", "|---|---|"]
    for cat in cat_order:
        if cat in tree:
            rep.append(f"| {cat} | {sum(len(v) for v in tree[cat].values())} |")
    rep.append("\n> 规则未命中的链接被归入『其他』或按域名自适应聚类；可通过编辑 "
               "categories.json 追加域名/关键词规则后重新运行，分类即更新。\n")
    with open(prefix + "_整理报告.md", "w", encoding="utf-8") as f:
        f.write("\n".join(rep))

    print("[6/6] 验证 ...")
    verify_html(out_html, len(keep))
    print(f"\n完成! 产物: {out_html}、{prefix}_整理报告.md、{prefix}_失效清单.csv、"
          f"{prefix}_存疑清单.csv、{prefix}_重复清单.csv")


if __name__ == "__main__":
    main()
