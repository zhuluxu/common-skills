## Context

当前 `paper-search-reader` 是一个 Claude Code skill，SKILL.md 仅描述了"给定 arXiv URL → 下载源码 → 阅读 → 生成报告"的单篇论文阅读流程。项目目录中已有从 `evil-read-arxiv/start-my-day` 迁移过来的 4 个 Python 脚本：

- `scripts/search_arxiv.py` — arXiv API + Semantic Scholar API 混合搜索、XML 解析、多维评分
- `scripts/scan_existing_notes.py` — 扫描 Obsidian vault 笔记构建关键词索引
- `scripts/link_keywords.py` — 在 Markdown 文本中自动将关键词替换为 wikilink
- `scripts/common_words.py` — 通用词过滤表

脚本功能完善，但 SKILL.md 未引用它们，用户无法通过 skill 触发论文搜索。

**约束**：
- SKILL.md 是 Claude Code 的指令文件，不是代码——它描述 AI 应执行的工作流
- 脚本已经可用，无需重写，只需在 SKILL.md 中正确调用
- 需要用户提供或配置 `research_interests.yaml` 路径

## Goals / Non-Goals

**Goals:**
- 在 SKILL.md 中整合完善的论文搜索工作流，让用户通过 `/paper-reader` 即可触发搜索
- 支持两种模式：(1) 搜索模式——自动搜索、筛选、评分论文 (2) 阅读模式——给定 URL 深度阅读单篇
- 搜索模式使用 `search_arxiv.py` 脚本完成 arXiv + Semantic Scholar 混合搜索
- 保留原有的单篇阅读能力不变
- 输出结构化的筛选结果（JSON），供用户或后续流程消费

**Non-Goals:**
- 不重写 Python 脚本（它们已经完善）
- 不实现推荐笔记生成（那是 `start-my-day` 的职责，本 skill 只负责搜索和阅读）
- 不实现图片提取或深度分析报告（那些是独立的 skill）
- 不修改 Obsidian vault 结构

## Decisions

### 1. SKILL.md 双模式设计：搜索 vs 阅读

**选择**：SKILL.md 根据用户输入自动判断模式——如果用户给了 arXiv URL 则进入阅读模式，否则进入搜索模式。

**替代方案**：
- 拆分为两个独立 skill（paper-search + paper-reader）→ 拒绝，因为搜索和阅读是同一个研究工作流的两个阶段
- 用子命令区分（`/paper-reader search` vs `/paper-reader read`）→ 可行但增加用户认知负担

**理由**：最自然的交互是"我给你 URL 你就读，我不给 URL 你就帮我找"。

### 2. 配置文件路径解析

**选择**：支持三种方式获取配置路径：
1. 用户在对话中显式指定
2. 环境变量 `OBSIDIAN_VAULT_PATH` + 约定路径 `99_System/Config/research_interests.yaml`
3. 默认使用脚本内置的默认配置

**理由**：灵活性——不同环境下用户可能有不同偏好。

### 3. 脚本调用方式

**选择**：在 SKILL.md 中通过 `cd "$SKILL_DIR" && python scripts/search_arxiv.py ...` 调用，与 `start-my-day` 保持一致。

**替代方案**：直接在 SKILL.md 中用伪代码描述搜索逻辑 → 拒绝，因为脚本已经实现了完整的 API 调用、XML 解析、评分算法，用自然语言描述既冗余又容易出错。

### 4. 搜索结果不生成 Obsidian 笔记

**选择**：搜索结果仅输出为 JSON 文件和终端摘要，不自动生成 Obsidian 推荐笔记。

**理由**：生成推荐笔记需要 Obsidian vault 路径、笔记模板、wikilink 格式等复杂逻辑。这些属于 `start-my-day` 的职责。`paper-search-reader` 聚焦于"搜索+阅读"两个核心能力。

## Risks / Trade-offs

- **[arXiv API 限流]** → 脚本已有指数退避重试（3次）；SKILL.md 中提示用户搜索可能需要等待
- **[Semantic Scholar API 429]** → 脚本已有 10s 等待重试；可通过配置 API key 缓解
- **[配置文件不存在]** → 脚本会回退到内置默认配置（通用 AI/ML 领域）；SKILL.md 中提示用户配置
- **[脚本依赖 PyYAML]** → 如果未安装，搜索模式无法运行；SKILL.md 中列出依赖并提示安装
