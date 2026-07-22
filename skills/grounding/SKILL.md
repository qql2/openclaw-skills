---
name: "grounding"
description: "Hallucination prevention: RAG grounding, web search verification, source citation, and refusal rules for factual reliability"
---

# Grounding Skill — Hallucination Prevention

This skill defines how to use `web_search`, `web_fetch`, and other retrieval tools to ground responses in verified sources and avoid hallucination.

## Core Principle

**Every factual assertion must have a traceable source.** If you cannot find a source via search or file reads, either mark the assertion as uncertain or refuse to answer.

---

## 1. The Grounding Workflow

When asked a question that involves facts, data, events, or technical details:

```
Step 1: Can I answer from workspace files or memory?
  YES → read the files, cite them
  NO  → go to Step 2

Step 2: Does the question need real-time / external info?
  YES → web_search (or web_fetch for known URLs)
  NO  → answer from model knowledge, mark as ❓ Uncertain

Step 3: web_search returned results?
  YES → web_fetch the most relevant links, extract facts
  NO  → refuse to answer: "我没搜到相关信息" or "I couldn't find information on that"

Step 4: Integrate retrieved facts into response with inline citations
```

## 2. Search Strategy

### Multi-Query Search
For complex questions, issue **multiple parallel searches** with different phrasings:
- One broad query
- One specific/technical query
- One in Chinese if the user asked in Chinese

### Source Selection
- Prefer **primary sources** (official docs, specs, papers) over aggregated content
- For code/API questions, prefer official docs > Stack Overflow > blog posts
- For news/events, prefer multiple corroborating sources

## 3. Citation Format

Inline citations attached to each factual claim:

```
[来源: web_search "query" — title URL]
[来源: 文件 skills/xxx.md line 42]
[来源: gh api response]
```

When using web sources, include:
- Brief description (title/site name)
- URL (when appropriate for the platform)
- Multiple sources for key facts: [来源1 + 来源2]

## 4. Refusal & Uncertainty

### When to Refuse
- Search returned nothing relevant
- Web fetch failed / returned error
- Tool call returned empty or error
- You genuinely don't know

### Refusal Language (Chinese)
- "抱歉，我没有找到关于这个问题的可靠信息。"
- "我搜索了一下，没有发现相关结果。"
- "这个信息超出了我的能力范围。"

### Refusal Language (English)
- "I couldn't find reliable information on that."
- "My search didn't return any relevant results."
- "I don't have enough information to answer that accurately."

## 5. Self-Verification (Faithfulness Check)

Before responding with factual content, run this mental checklist:

```
✅ Every data point / date / name / number has a source?
✅ I didn't "smooth over" gaps with plausible details?
✅ I actually checked the search results (not just assumed)?
✅ Tool errors are reported honestly?
✅ I'm not answering from training data alone without marking it?
```

If any answer is "no" → fix before sending.

## 6. Combining Multiple Sources

When information from different sources conflicts:
- Present both sides: "来源 A 说 X，但来源 B 说 Y"
- Note which source is more authoritative
- Don't silently pick the one that sounds better

## 7. Technical / Code Grounding

For code-related questions:
- **API endpoints**: verify with web_search or file read before stating
- **Function signatures**: verify, don't guess parameter names
- **Configuration**: read the actual config file, don't infer
- **Package versions**: check actual versions, don't assume latest

---

## When Not to Use This Skill

- Casual conversation, opinions, humor
- Meta-commentary about the system or the conversation
- Pure reasoning / logic tasks where no external facts are involved
- Tasks where the user explicitly says "just your opinion" or "what do you think"
