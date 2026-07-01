---
name: "bilibili-comment-summary"
description: "Fetch bilibili comments, analyze into essay-style arguments, generate interactive HTML report, publish to GitHub."
---

# B站视频评论总结

## Goal
当用户要求总结 B站视频的评论区时，抓取 60 条热门评论，分析提炼为 4-5 个段落式论点，每条评论归入对应论点，生成交互式 HTML 报告并发布预览链接。

## 前置条件
- `~/MediaCrawler` 已安装且依赖完备
- 已通过 MediaCrawler 完成 B 站登录（cookie 持久化在 browser_data）
- 代码仓库：`~/.openclaw/workspace` 下的 `bilibili-comment-bridge.py` + `comment_report.py`

## 完整工作流

### Step 1: 解析 BVID
```
re.search(r'BV[a-zA-Z0-9]+', url) → bvid
```

### Step 2: 爬取评论（exec 调用，不耗 LLM token）
```bash
cd ~/MediaCrawler
python3 ~/.openclaw/workspace/bilibili-comment-bridge.py <BVID> --count 60
```
- 清理 `SingletonLock`
- 调用 MediaCrawler detail 模式
- Playwright headless + WBI 签名 → `/x/v2/reply/wbi/main`
- 子回复（ps=30）→ `/x/v2/reply/reply`
- 写入 `data/bili/jsonl/detail_comments_YYYY-MM-DD.jsonl`
- **注意：MediaCrawler 可能在 stdout 无输出的情况下完成抓取（静默成功）**。若命令退出后 `detail_comments_YYYY-MM-DD.jsonl` 文件存在且有内容，则视为成功，可继续 Step 3

### Step 3: 加载结构化数据（exec 调用，不耗 LLM token）
```bash
python3 ~/.openclaw/workspace/comment_report.py <BVID> --count 60
```
- 调用 `comment_report.py` 的 CLI 模式
- 自动读取 JSONL 文件、去重、按点赞排序、子回复归组
- 通过 API 获取标题 / UP主 / 点赞数
- 返回标准 JSON 结构给 LLM 分析：
  ```json
  {
    "video": { "title": "...", "bvid": "BV...", "owner": "...", "likes": "12345" },
    "comments": [
      { "id": "123", "content": "...", "like": 123, "nickname": "...",
        "subs": [{"content":"...","nickname":"...","like": 12}, ...],
        "sub_total": 5
      },
      ...
    ]
  }
  ```
- **不再需要 LLM 写代码读数据**，一次 exec 调用拿到全部结构化数据

### Step 4: 分析评论 → 提炼论点（唯一的 LLM 步骤）
基于 Step 3 返回的 JSON 数据，逐条阅读 60 条评论（含子回复），提炼 4-5 个段落式论点：
- 每个论点像作文段落：有中心观点、有分析论证
- 每条评论（60/60）分配到一个论点，不重复、不遗漏
- 论点标题简洁有力，段落约 150-250 字

注意：这一步是**唯一消耗 token 的步骤**。不要写代码、不要调 API，直接在大脑里分析评论数据。

#### 输出格式：只输出论点结构，不嵌评论对象
大模型只需要输出轻量级的论点结构，**不要**把完整的评论对象嵌入 JSON：
```json
{
  "bvid": "BV1PNigB4Ejp",
  "video": {
    "title": "视频标题"
  },
  "arguments": [
    {
      "title": "论点标题",
      "summary": "段落式分析文本，使用中文弯引号「」而不是英文双引号"",
      "comment_ids": ["285045241409", "287118376464"]
    }
  ]
}
```
- `comment_ids` 是字符串数组，值从 Step 3 输出的每条评论的 `id` 字段获取
- **禁止**嵌完整评论对象——程序会帮你合并
- 这样生成的 JSON 极其轻量，且不会出现引号冲突问题

### Step 5: 生成 HTML 报告并发布（exec 管道调用，不耗 LLM token）
将 Step 4 的分析结果（轻量论点结构：title + summary + comment_ids）传给 `comment_report.py --gen-report`，
程序会自动合并 Step 3 持久化的评论数据，生成完整 HTML。

```bash
# Step 3 的输出已自动写入 /tmp/<BVID>.data.json
# Step 4 的 LLM 分析结果通过文件传入：
echo '<论点分析 JSON>' > /tmp/<BVID>.analysis.json

python3 ~/.openclaw/workspace/comment_report.py --gen-report \
  --analysis /tmp/<BVID>.analysis.json
```

程序自动完成：
1. 读取 `/tmp/<BVID>.data.json`（Step 3 持久化的评论数据）
2. 读取论点 JSON 中的 `comment_ids`，从评论数据中查找对应评论
3. 合并生成完整 HTML
4. 推送到 `qql2/bilibili-tools/reports/`
5. 返回 HTMLPreview 预览链接

#### 论点分析 JSON 格式（LLM 输出）
```json
{
  "bvid": "BV1PNigB4Ejp",
  "video": {
    "title": "视频标题"
  },
  "arguments": [
    {
      "title": "论点标题",
      "summary": "段落式分析文本，使用中文弯引号「」而不是英文双引号",
      "comment_ids": ["285045241409", "287118376464"]
    }
  ]
}
```
- `comment_ids` 是字符串数组，对应 Step 3 输出的评论 id
- **不需要**嵌完整评论对象，程序负责合并
- `summary` 字段建议使用中文弯引号 `「」` 代替英文 `"`，不过即使用了英文引号也不影响 JSON 结构，因为这里不再拼接嵌对象的大型 JSON

**不再需要 LLM 写 HTML 生成代码，也不再需要构建嵌对象的大型 JSON**，一次简单的文件 pipe 完成全部发布。

#### BVID 不一致时怎么办
如果 Step 4 的论点 JSON 中 `bvid` 与 Step 3 持久化的文件不匹配，程序会报警告但继续尝试。
你可以显式指定数据文件：
```bash
python3 ~/.openclaw/workspace/comment_report.py --gen-report \
  --analysis /tmp/analysis.json \
  --data /tmp/BVxxx.data.json
```

### Step 6: 测量本次任务 Token 消耗

在任务开始前和结束后各调一次 `session_status`，取差值：

```
📊 本次任务 Token 消耗
输入:  XXX tokens
输出:  XXX tokens
缓存:  XXX (命中率 XX%)
耗时:  XX 秒
```

测量方式：
1. 任务开始时记录 `session_status` 的 Tokens 计数
2. 执行 Step 2-5
3. 任务结束时再次调用 `session_status`
4. 计算差值 = 本次任务实际消耗

注意：`session_status` 返回的是 OpenClaw 从 Provider API 响应中解析的真实数据，不是模型估算。

### Step 7: 回复用户预览链接 + Token 消耗
```
📊 本次任务 Token 消耗
输入:  XXX tokens | 输出: XXX tokens
缓存:  XXX (命中率 XX%) | 耗时:  XX 秒

https://htmlpreview.github.io/?https://raw.githubusercontent.com/qql2/bilibili-tools/<commit>/reports/<BVID>.html
```

## 论点评分标准

每条论点应满足：
- 有明确的中心观点（一个完整的 thesis）
- 有足够的支撑评论（至少 8-15 条）
- 段落有分析、有推理，不只是罗列评论
- 覆盖用户深层情绪（玩梗、焦虑、反思等）

## 报告结构

```
📹 视频标题
👤 UP主：XXX | BVID：BVxxxx

论点一：标题（段落式分析）
  ▶ [赞数👍] 用户名: 评论原文 + 子回复 + 原文链接
  ▶ ...

论点二：标题（段落式分析）
  ▶ ...
```

## 数据链路

```
用户 → "总结这个"
  │
  ├─ Step 2: bilibili-comment-bridge.py     (exec，0 token)
  │     → MediaCrawler detail 模式
  │     → Playwright + WBI 签名
  │     → JSONL 文件
  │
  ├─ Step 3: comment_report.py --count 60   (exec，0 token)
  │     → 去重、排序、子回复归组
  │     → 标准 JSON 输出
  │
  ├─ Step 4: LLM 分析                        (唯一消耗 token 的步骤)
  │     → 逐条阅读 60 条评论
  │     → 提炼 4-5 个论点
  │     → 每条评论分配归位
  │
  └─ Step 5: comment_report.py --gen-report  (exec 管道，0 token)
        → generate_html()
        → publish_to_repo()
        → 返回预览链接
```

## 已提交仓库
- `github.com/qql2/bilibili-tools` — 桥接脚本 + 报告生成 + reports/
- `github.com/qql2/MediaCrawler` — fork，含子评论优化和 bug 修复

## 注意事项
- 首次需扫码登录（`--headless no`），cookie 持久化后无需重复操作
- 子回复不独立分配论点，只作为上下文辅助理解
- 60 条是默认值，可通过 `--count` 调整
