---
name: "obsidian-knowledge-base-guide"
description: "Guide for the AI to operate the user's Obsidian personal knowledge base vault"
---

# Obsidian 个人知识库交互指南

## When to Activate

Activate this skill when the user mentions their Obsidian vault, personal knowledge base, notes system, or knowledge management. Also activate when working with files in the `ob` repository (the Obsidian vault).

## Configuration

- **Vault repository**: `ob` (private repo, GitHub user `qql2`)
- **Vault root**: The root of this repo is the vault root
- **Access method**: Use `gh api repos/qql2/ob/contents/<path>` to read files from the vault
- **File path convention**: All paths below are relative to the vault repo root

## Core Rules

### 1. Knowledge Base Philosophy
- This is a personal knowledge base that emphasizes **connections between knowledge points**
- It is built on **constructivist learning theory** — new knowledge builds on existing knowledge
- Each note should be part of a web, not an isolated document
- For the complete architecture and philosophy, READ the knowledge base architecture document:
  `笔记/问题导向的方法/电子软件大类问题/qql1笔记体系/qql1个人知识库体系.md`

### 2. Bidirectional Links (双链)
- When creating new nodes/notes, **always use bidirectional links** to connect related knowledge points
- Use `[[wikilinks]]` format to reference related notes
- However, **ensure link validity**: do NOT create links pointing to non-existent files
  - Either create the corresponding file for the linked topic, or omit the link entirely
- For the types of links to use, READ the link types document:
  `笔记/问题导向的方法/电子软件大类问题/qql1笔记体系/link的类型.md`

### 3. Avoid Redundancy — Search Before Adding
- Before adding new knowledge, **search the repository** to confirm whether similar or related knowledge points already exist
- If duplicates or conflicts are found:
  - **Flag them to the user** and let them choose how to resolve the conflict
  - Do NOT silently merge or overwrite
- Minimize redundancy:
  - Check whether similar notes already exist
  - Merge or reuse existing notes where appropriate
- For the full set of note-keeping principles, READ the note principles document:
  `笔记/问题导向的方法/电子软件大类问题/qql1笔记体系/qql1笔记原则.md`

### 4. The 80/20 Rule for Content
When adding new content, follow this structure:

- **First 20%** — Overview of the most important content:
  - NOT like an encyclopedia (no lengthy walls of text)
  - Be **extremely concise and easy to understand**, as if teaching a child
  - Use **short examples** for intuitive explanation
- **Remaining 80%** — In-depth coverage of the remaining content

## How to Read the Referenced Files

When the skill references a path like `笔记/问题导向的方法/电子软件大类问题/qql1笔记体系/qql1个人知识库体系.md`, use the `gh` CLI to fetch it:

```bash
gh api repos/qql2/ob/contents/<path-to-file> --jq '.content' | base64 -d
```

For example, to read the knowledge base architecture:
```
gh api repos/qql2/ob/contents/笔记/问题导向的方法/电子软件大类问题/qql1笔记体系/qql1个人知识库体系.md --jq '.content' | base64 -d
```

Read these files whenever deeper context is needed — don't guess or assume what they contain.

## Origin
This skill originates from `.github/prompts/个人知识库ai使用指南.prompt.md` in the `ob` repository, originally created to guide Cursor AI when working with the personal knowledge base.
