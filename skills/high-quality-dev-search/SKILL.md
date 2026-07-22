---
name: "high-quality-dev-search"
description: "优先使用高可信来源检索技术信息，避免 SEO 噪音"
---

---
name: high-quality-dev-search
description: "优先使用高可信来源检索技术信息，避免 SEO 噪音"
metadata:
  keywords: ["developer-sources", "tech-search", "quality-scoring"]
---

# 程序员高质量信息来源检索

## 触发条件

当以下场景出现时，**必须触发**此 skill 替代普通 web_search：

### 明确触发（必须使用）

1. **用户提出具体技术问题**
   - "React 的 useEffect 和 useLayoutEffect 有什么区别"
   - "Go 语言的 GC 是怎么工作的"
   - 任何编程语言/框架/工具的使用或原理问题

2. **需要验证/引用技术事实**
   - API 的正确用法
   - 某项功能的兼容性
   - 某个版本的变更记录

3. **需要最佳实践 / 架构决策参考**
   - 微服务拆分策略
   - 状态管理方案对比
   - Docker 镜像优化

4. **需要中文技术内容**
   - 用户明确要求中文资料
   - 涉及国内技术生态（如微信小程序、飞书、阿里云等）

### 可选触发（推荐使用）

5. **搜索新技术/新框架**
   - 替代普通 web_search，优先从 GitHub Issues/PR、官方文档、工程博客获取

6. **评估开源方案**
   - 替代在搜索结果中乱翻，直接去 GitHub Trending + Issues + SourceGraph

7. **调试/排错**
   - Stack Overflow + GitHub Issues（workaround 楼层）往往比普通搜索更快找到答案

### 不触发的情况

- 非技术类查询（天气、新闻、娱乐）
- 用户明确要求普通 web_search
- 仅需模型知识即可回答的常识性问题

---

## 基础规则

### 可信度分级

| 等级 | 含义 | 适用 |
|---|---|---|
| ✅ 最高权威 | 官方标准/文档 | MDN, IEEE, ACM, arXiv, 官方 docs |
| ✅ 高 | 知名社区+审核/知名个人 | Stack Overflow, Smashing Magazine, Martin Fowler |
| 📎 中高 | 有质量但需甄别 | Dev.to, Hacker News, 掘金优质作者 |
| 📎 中 | 信息量大但混杂 | V2EX, CSDN, Reddit 子版块 |

### 来源引用要求

每个事实性断言必须附带可验证来源链接：
- 文件路径直接引用
- GitHub 仓库 URL + 文件路径
- 网页来源 URL

---

## 1. 权威文档 — 最高优先级

| 领域 | 来源 | URL | 搜索方式 |
|---|---|---|---|
| Web 标准 | MDN Web Docs | developer.mozilla.org | 直接 fetch 文档页面 |
| .NET/Azure | Microsoft Learn | learn.microsoft.com | 官方 API 参考 |
| Web 性能 | web.dev | web.dev | Google 官方 |
| React | React Docs | react.dev | 官方文档 |
| Vue | Vue Docs | vuejs.org | 官方文档 |
| Python | Python Docs | docs.python.org | `/3/` |
| Rust | Rust Docs | doc.rust-lang.org | 标准库参考 |
| TypeScript | TS Docs | typescriptlang.org/docs | 官方手册 |

## 2. 经典问答社区

- **Stack Overflow** — AI 搜索走 `site:stackoverflow.com` + 关键词
- **Server Fault** — 服务器运维
- **Software Engineering SE** — 架构决策、设计模式
- **CS Stack Exchange** — 算法、复杂度

> ⚠️ Stack Exchange 系列有 Cloudflare 防护，curl/fetch 可能返回 403，建议用 `site:` 搜索方式。

## 3. 个人/团队技术博客

### 国际（高可信）
- Julia Evans (jvns.ca) — 系统/网络/调试
- Martin Fowler (martinfowler.com) — 架构/重构/DDD
- CSS-Tricks (css-tricks.com) — 前端
- Smashing Magazine (smashingmagazine.com) — 前端/UX
- Overreacted (overreacted.io) — React 底层
- Cloudflare Blog (blog.cloudflare.com) — 网络/安全
- Netflix Tech Blog (netflixtechblog.com) — 大规模分布式
- GitHub Blog (github.blog) — 开源/DevOps/AI
- 2ality (2ality.com) — JS/TS 深度
- Joel on Software (joelonsoftware.com) — 软件管理经典
- The Old New Thing (devblogs.microsoft.com/oldnewthing) — Windows 底层

### 中文
- 张鑫旭博客 (zhangxinxu.com/wordpress) — CSS/前端 ✅ 200
- 廖雪峰博客 (liaoxuefeng.com) — Python/Java/Git ✅ 200
- 美团技术团队 (tech.meituan.com) — 后端/架构 ✅ 200
- 阮一峰的网络日志 — 综合技术周刊 ⚠️ Cloudflare，需走浏览器

## 4. 技术新闻 & 深度分析

- **Hacker News** (news.ycombinator.com) — Algolia 搜索：`hn.algolia.com`
- **InfoQ** (infoq.com) — 架构/云原生/DevOps ⚠️ 有反爬
- **Ars Technica** (arstechnica.com) — 科技深度报道 ✅ 200
- **MIT Technology Review** (technologyreview.com) — 前沿科技 ✅ 200
- **LWN.net** (lwn.net) — Linux 内核/开源 ✅ 200
- **IEEE Spectrum** (spectrum.ieee.org) — 工程技术 ✅ 200
- **InfoQ 中文** (infoq.cn) — 中文技术趋势 ✅ 200

## 5. 学术 & 前沿研究

- **arXiv** (arxiv.org) — 搜索 `arxiv.org + 关键词`
- **Papers With Code** (paperswithcode.com) — 论文 + 实现代码
- **Semantic Scholar** (semanticscholar.org) — AI 论文语义搜索
- **Google Scholar** (scholar.google.com) — 引用数排序
- **DBLP** (dblp.org) — 论文元数据库

## 6. 开源 & 代码发现

- **GitHub Trending** (github.com/trending) — 每日热门
- **GitHub Explore** (github.com/explore) — 主题精选
- **SourceGraph** (sourcegraph.com) — 代码语义搜索

## 7. GitHub Issues & PR（隐藏金矿）

包含大量真实世界的工程信息：

- **Bug report** — 真实复现步骤、堆栈日志
- **RFC / Feature request** — 维护者的架构决策、trade-off
- **Closed as wontfix** — 反面架构课
- **Workaround 楼层** — 官方没修但社区有绕行方案
- **PR conversations** — 代码级别的设计讨论

推荐追的项目 Issues（以教参目的）：
`nodejs/node`, `microsoft/vscode`, `vercel/next.js`, `rust-lang/rust`, `vuejs/core`, `facebook/react`

搜索模式：
```
site:github.com/{owner}/{repo}/issues "design decision"
site:github.com/{owner}/{repo}/pulls "motivation" OR "rationale"
```

## 8. RSS 聚合源

- Hacker News RSS (hnrss.org/frontpage)
- Lobsters RSS (lobste.rs/rss)
- EchoJS (echojs.com) — JS 社区
- A List Apart (alistapart.com) — Web 设计

---

## 检索策略

### 按场景的搜索路径

```
1. 具体技术问题
   → site:stackoverflow.com + 关键词
   → 或直接 fetch 相关 MDN 文档

2. 前沿趋势 / 论文
   → ArXiv + Semantic Scholar + Papers With Code
   → Hacker News 评论中的讨论

3. 最佳实践 / 架构决策
   → Martin Fowler + InfoQ + 公司 engineering blog
   → React/Node 官方 blog

4. 开源方案评估
   → GitHub Trending + GitHub Issues/Discussions
   → SourceGraph 代码搜索

5. 中文内容优先
   → 阮一峰 / 美团技术 / 掘金
   → V2EX 讨论帖 / InfoQ 中文

6. 代码级别的决策细节
   → GitHub Issues/PR（RFC / design decision 标签）
   → SourceGraph 代码搜索

7. 系统底层 / 网络
   → LWN.net / Julia Evans / Cloudflare Blog
   → Rust/LLVM 官方 Blog
```

### 反爬处理

以下站点在 curl/web_fetch 时可能返回 403/405，但浏览器可正常访问：
- Stack Overflow（Cloudflare）
- Reddit（所有子版块）
- 阮一峰博客（Cloudflare）
- Phoronix
- InfoQ
- ACM Digital Library / O'Reilly（付费墙）

AI agent 层面策略：使用 `site:` 搜索方式代替直接 fetch，或走浏览器渲染。
