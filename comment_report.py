#!/usr/bin/env python3
"""comment_report.py — B站评论区观点分析 HTML 报告生成器"""
import json, os, subprocess, sys, tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

MEDIACRAWLER_DIR = os.path.expanduser("~/MediaCrawler")
DATA_DIR = os.path.join(MEDIACRAWLER_DIR, "data", "bili", "jsonl")

def _read_jsonl(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def _find_today(prefix):
    for d in [0, -1]:
        ds = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
        p = os.path.join(DATA_DIR, f"{prefix}_{ds}.jsonl")
        if os.path.exists(p): return p
    return ""

def load_comments(aid, max_top=60):
    raw = _read_jsonl(_find_today("detail_comments"))
    if not raw: raw = _read_jsonl(_find_today("search_comments"))
    raw = [c for c in raw if str(c.get("video_id", "")) == aid]
    pool = {}
    for c in raw:
        cid = str(c["comment_id"])
        if cid not in pool: pool[cid] = c
    by_parent = defaultdict(list)
    for c in pool.values():
        by_parent[str(c.get("parent_comment_id", "0"))].append(c)
    top = []
    for c in by_parent.get("0", []):
        cid = str(c["comment_id"])
        subs = by_parent.get(cid, [])
        top.append({
            "id": cid,
            "content": c.get("content", ""),
            "like": int(c.get("like_count", 0) or 0),
            "nickname": c.get("nickname", "匿名"),
            "subs": [
                {"content": s.get("content",""), "nickname":s.get("nickname","匿名"),
                 "like": int(s.get("like_count",0) or 0)}
                for s in sorted(subs, key=lambda x:int(x.get("like_count",0) or 0), reverse=True)[:15]
            ],
            "sub_total": len(subs),
        })
    top.sort(key=lambda x: x["like"], reverse=True)
    return top[:max_top]

def _esc(s):
    """Escape HTML special chars"""
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def generate_html(title, owner, bvid, likes, fetched, arguments):
    """arguments: [{title, summary, comments}]"""
    css = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f5;color:#333;line-height:1.6;padding:20px}
.w{max-width:800px;margin:0 auto}
.hd{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.hd h1{font-size:20px;margin-bottom:8px;color:#00a1d6}
.hd .m{font-size:14px;color:#666}
.st{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;font-size:13px;color:#888}
.ar{background:#fff;border-radius:12px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.1);overflow:hidden}
.ah{padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:flex-start;user-select:none}
.ah:hover{background:#fafafa}
.at{font-size:17px;font-weight:600;color:#222}
.as{font-size:14px;color:#666;margin-top:4px}
.bd{background:#00a1d6;color:#fff;border-radius:20px;padding:2px 10px;font-size:12px;white-space:nowrap}
.tg{font-size:14px;color:#999;margin-left:8px}
.ab{display:none;padding:0 20px 16px;border-top:1px solid #eee}
.ab.o{display:block}
.cc{background:#f9f9f9;border-radius:8px;padding:12px;margin-top:10px;border-left:3px solid #00a1d6}
.cm{font-size:12px;color:#888;margin-bottom:4px}
.lk{color:#f73131;font-weight:600}
.ct{font-size:14px;margin-bottom:6px;white-space:pre-wrap}
.cl{font-size:12px;color:#00a1d6;text-decoration:none}
.cl:hover{text-decoration:underline}
.sb{margin-top:8px;padding-left:12px;border-left:2px solid #ddd;font-size:13px;color:#555}
.si{margin:4px 0}
.sn{color:#888}
.ft{text-align:center;font-size:12px;color:#aaa;margin:20px 0}
"""
    args_html = ""
    for i, a in enumerate(arguments, 1):
        cards = ""
        for c in a["comments"]:
            link = f"https://www.bilibili.com/video/{bvid}#reply{c['id']}"
            subs = ""
            if c.get("subs"):
                items = "".join(
                    f'<div class=si><span class=sn>{_esc(s["nickname"])}</span>: {_esc(s["content"])}</div>'
                    for s in c["subs"]
                )
                extra = c.get("sub_total", 0) - len(c["subs"])
                if extra > 0:
                    items += f'<div class=si style=color:#aaa>└ 还有 {extra} 条子回复</div>'
                subs = f'<div class=sb>{items}</div>'
            cards += f'''<div class=cc>
<div class=cm><span class=lk>❤ {c["like"]}</span> &nbsp; {_esc(c["nickname"])}</div>
<div class=ct>{_esc(c["content"][:300])}</div>
<a class=cl href="{link}" target=_blank>🔗 查看原文</a>{subs}</div>'''
        args_html += f'''<div class=ar>
<div class=ah><div><div class=at>{i}. {_esc(a["title"])}</div>
<div class=as>{_esc(a["summary"])}</div></div>
<div style=text-align:right;flex-shrink:0>
<span class=bd>{len(a["comments"])} 条</span><span class=tg>▼</span></div></div>
<div class=ab>{cards}</div></div>'''

    return f'''<!DOCTYPE html>
<html lang=zh-CN>
<head><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1.0">
<title>{_esc(title)} — 评论观点分析</title><style>{css}</style></head>
<body>
<div class=w>
<div class=hd>
<h1>📹 {_esc(title)}</h1>
<div class=m>👤 UP主：{_esc(owner)} &nbsp;|&nbsp; BVID：{bvid}</div>
<div class=st><span>👍 {likes}</span><span>💬 分析来源：{fetched} 条热门评论</span></div>
</div>
{args_html}
<div class=ft>数据来源：Bilibili API via MediaCrawler | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</div>
<script>
document.querySelectorAll('.ah').forEach(function(h){{
h.addEventListener('click',function(){{
var b=h.nextElementSibling;b.classList.toggle('o');
h.querySelector('.tg').textContent=b.classList.contains('o')?'▲':'▼';
}})
}})
</script>
</body>
</html>'''

def publish_to_repo(html, filename, bvid):
    """推送 HTML 到 bilibili-tools/reports/，返回可预览链接"""
    repo = os.path.expanduser("~/.openclaw/workspace/bilibili-tools")
    os.makedirs(f"{repo}/reports", exist_ok=True)
    path = f"{repo}/reports/{filename}"
    with open(path, "w") as f: f.write(html)
    subprocess.run(["git","add",f"reports/{filename}"], cwd=repo, capture_output=True)
    subprocess.run(["git","commit","-m",f"report: {bvid} 评论观点分析"], cwd=repo, capture_output=True)
    subprocess.run(["git","push","origin","main"], cwd=repo, capture_output=True, timeout=15)
    # 用 commit hash 绕过 CDN 缓存
    r = subprocess.run(["git","rev-parse","HEAD"], cwd=repo, capture_output=True, text=True)
    sha = r.stdout.strip()
    raw = f"https://raw.githubusercontent.com/qql2/bilibili-tools/{sha}/reports/{filename}"
    return f"https://htmlpreview.github.io/?{raw}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="B站评论观点分析报告工具")
    parser.add_argument("bvid", nargs="?", help="BVID 或视频URL")
    parser.add_argument("--count", type=int, default=60, help="拉取评论数")
    parser.add_argument("--gen-report", action="store_true",
                        help="生成并发布 HTML 报告：从 stdin 读取分析结果 JSON，输出预览链接")
    args = parser.parse_args()

    if args.gen_report:
        # --gen-report 模式：从 stdin 读取分析结果 JSON
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            context = raw[max(0, e.pos-60):e.pos+60]
            print(f"❌ --gen-report 输入的 JSON 解析失败（行 {e.lineno} 列 {e.colno}）", file=sys.stderr)
            print(f"  常见原因：中文引号用了 ASCII 双引号「\"」而非 JSON 字符串的转义格式", file=sys.stderr)
            print(f"  解决：使用 Python json.dumps(ensure_ascii=False) 构建 JSON，不要手写", file=sys.stderr)
            print(f"  --- 错误位置上下文 ---", file=sys.stderr)
            print(f"  {context}", file=sys.stderr)
            print(f"  ---", file=sys.stderr)
            sys.exit(1)
        title = data["video"]["title"]
        bvid = data["video"]["bvid"]
        owner = data["video"]["owner"]
        likes = str(data["video"]["likes"])
        fetched = len(data["comments"])
        arguments = data["arguments"]
        html = generate_html(title, owner, bvid, likes, fetched, arguments)
        url = publish_to_repo(html, f"{bvid}.html", bvid)
        print(url)
        sys.exit(0)

    # 原有模式：加载评论数据，输出 JSON
    import urllib.request as ureq
    vi = json.loads(ureq.urlopen(ureq.Request(f"https://api.bilibili.com/x/web-interface/view?bvid={args.bvid}",
        headers={"User-Agent":"Mozilla/5.0"}),timeout=10).read().decode()).get("data",{})
    title,owner,likes = vi.get("title","?"),vi.get("owner",{}).get("name","?"),str(vi.get("stat",{}).get("like",0))
    aid = str(vi.get("aid",""))
    comments = load_comments(aid, max_top=args.count)
    if not comments:
        print(json.dumps({"error":"No comments found"})); sys.exit(1)
    print(json.dumps({"video":{"title":title,"bvid":args.bvid,"owner":owner,"likes":likes},"comments":comments},ensure_ascii=False))
