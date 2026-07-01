#!/usr/bin/env python3
"""
bilibili-comment-bridge.py — OpenClaw ↔ MediaCrawler 桥接脚本

用法：
    python3 bilibili-comment-bridge.py <BVID>              # 默认取 60 条
    python3 bilibili-comment-bridge.py <BVID> --count 20   # 只取 20 条
    python3 bilibili-comment-bridge.py <BVID> --count 200  # 取 200 条

前置条件：
    - ~/MediaCrawler 已安装且依赖已安装
    - 已通过 MediaCrawler 完成 B 站登录 (browser_data/bili_user_data_dir)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Optional, List

MEDIACRAWLER_DIR = os.path.expanduser("~/MediaCrawler")
VENV_PYTHON = os.path.join(MEDIACRAWLER_DIR, ".venv", "bin", "python3")
DATA_DIR = os.path.join(MEDIACRAWLER_DIR, "data", "bili", "jsonl")


def extract_bvid(text: str) -> Optional[str]:
    m = re.search(r"BV[a-zA-Z0-9]+", text)
    return m.group() if m else None


def run_crawler(bvid: str, max_comments: int = 60) -> bool:
    python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    main_py = os.path.join(MEDIACRAWLER_DIR, "main.py")
    print(f"🚀 正在启动 MediaCrawler (max={max_comments})...", file=sys.stderr, flush=True)
    try:
        result = subprocess.run(
            [python, main_py, "--platform", "bili", "--type", "detail",
             "--specified_id", bvid, "--headless", "yes",
             "--get_sub_comment", "yes",
             "--max_comments_count_singlenotes", str(max_comments)],
            cwd=MEDIACRAWLER_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print(f"⏰ MediaCrawler 超时（300s），但数据可能已部分写入", file=sys.stderr, flush=True)
        return True
    filtered = 0
    for line in result.stdout.split("\n"):
        if any(kw in line for kw in ["INFO", "WARN", "ERROR", "comment"]):
            print(f"  {line.strip()}", file=sys.stderr, flush=True)
            filtered += 1
    if filtered == 0:
        # 没有过滤到任何日志行，说明数据已经通过 Playwright 静默写入了
        print(f"📝 MediaCrawler 执行完成（stdout 无有效日志行，数据已写入 JSONL）", file=sys.stderr, flush=True)
    else:
        print(f"✅ MediaCrawler 执行完成（{filtered} 条日志）", file=sys.stderr, flush=True)
    if result.returncode != 0 and "SingletonLock" not in result.stderr:
        print(f"❌ 退出码: {result.returncode}", file=sys.stderr, flush=True)
        if result.stderr:
            print(f"  错误: {result.stderr[:300]}", file=sys.stderr, flush=True)
        return False
    return True


def read_jsonl(filename: str) -> List[dict]:
    if not os.path.exists(filename):
        return []
    with open(filename) as f:
        return [json.loads(line) for line in f if line.strip()]


def find_today_file(suffix: str) -> str:
    for offset in [0, -1]:
        d = (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")
        path = os.path.join(DATA_DIR, f"{suffix}_{d}.jsonl")
        if os.path.exists(path):
            return path
    return ""


def format_summary(vi: dict, comments: List[dict], bvid: str) -> str:
    lines = []
    lines.append("📊 B 站视频评论总结")
    lines.append("━" * 50)
    lines.append(f"📹 {vi.get('title', 'N/A')}")
    lines.append(f"👤 UP 主：{vi.get('nickname', 'N/A')}")
    lines.append(f"🎬 播放：{vi.get('video_play_count', '?')} | "
                 f"👍 点赞：{vi.get('liked_count', '?')}")
    lines.append(f"💬 评论：共获取 {len(comments)} 条")
    lines.append("")
    for i, c in enumerate(comments, 1):
        content = c.get("content", "")[:200]
        like = c.get("like_count", "0")
        nick = c.get("nickname", "匿名")
        cid = c.get("comment_id", "0")
        lines.append(f"#{i} [{like}👍] {nick}")
        lines.append(f"  「{content}」")
        lines.append(f"  🔗 https://www.bilibili.com/video/{bvid}#reply{cid}")
        lines.append("")
    lines.append("━" * 50)
    lines.append("数据来源：MediaCrawler (Bilibili API + WBI 签名)")
    lines.append(f"BVID: {bvid}")
    return "\n".join(lines)


def _bvid_to_aid(bvid: str) -> Optional[str]:
    """通过 B 站 API 把 BVID 转成 AID"""
    import urllib.request as _req, json as _json
    try:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        r = _req.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = _json.loads(_req.urlopen(r, timeout=10).read().decode())
        if data.get("code") == 0:
            return str(data["data"]["aid"])
    except Exception:
        pass
    return None


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="B站评论总结（基于 MediaCrawler）")
    parser.add_argument("video", help="BVID / URL")
    parser.add_argument("--count", type=int, default=60,
                        help="拉取条数 (default: 60)")
    parser.add_argument("--no-crawl", action="store_true",
                        help="只读已有数据")
    args = parser.parse_args(argv)

    bvid = extract_bvid(args.video)
    if not bvid:
        print(f"❌ 无法解析 BVID: {args.video}", file=sys.stderr)
        sys.exit(1)

    # 转成 AID 用于 JSONL 匹配
    target_aid = _bvid_to_aid(bvid)
    if not target_aid:
        print(f"❌ 无法获取视频 AID: {bvid}", file=sys.stderr)
        sys.exit(1)

    # 清理旧的 SingletonLock
    lockfile = os.path.join(MEDIACRAWLER_DIR, "browser_data",
                            "bili_user_data_dir", "SingletonLock")
    if os.path.exists(lockfile):
        os.remove(lockfile)

    if not args.no_crawl:
        ok = run_crawler(bvid, max_comments=args.count)
        if not ok:
            print("⚠️ 爬取失败，尝试读取已有数据...", file=sys.stderr)

    # 读取 JSONL，匹配目标视频的 AID
    contents = read_jsonl(find_today_file("detail_contents"))
    comments = read_jsonl(find_today_file("detail_comments"))
    if not contents and not comments:
        contents = read_jsonl(find_today_file("search_contents"))
        comments = read_jsonl(find_today_file("search_comments"))
    if not contents:
        print("❌ 未找到视频数据", file=sys.stderr)
        sys.exit(1)

    # 在 contents 中找到匹配目标 AID 的条目
    vi = None
    for c in contents:
        if c.get("video_id") == target_aid:
            vi = c
            break
    if not vi:
        # 降级：拿最新的
        print(f"⚠️ 未找到匹配 AID={target_aid} 的视频信息，使用最新一条", file=sys.stderr)
        vi = contents[-1]

    # 过滤属于该视频的评论
    target_id = vi.get("video_id", target_aid)
    video_comments = [c for c in comments if c.get("video_id") == target_id]

    # Dedup by comment_id
    seen = set()
    deduped = []
    for c in video_comments:
        cid = str(c.get("comment_id", ""))
        if cid not in seen:
            seen.add(cid)
            deduped.append(c)

    output = format_summary(vi, deduped, bvid)
    print(output)


if __name__ == "__main__":
    main()
