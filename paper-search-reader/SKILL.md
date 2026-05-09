---
name: paper-search-reader
description: 论文搜索与阅读 - 搜索arXiv/Semantic Scholar论文并筛选评分，或深度阅读单篇论文 / Paper search & read - search, filter, score papers from arXiv/Semantic Scholar, or deep-read a single paper
---

# 论文搜索与阅读 Skill

本 skill 提供两种核心能力：
1. **搜索模式**：根据研究兴趣自动搜索 arXiv 和 Semantic Scholar，筛选、多维评分并排序论文
2. **阅读模式**：深度阅读单篇论文，生成高质量 Obsidian 笔记（TeX 源码优先，PDF fallback）

# 模式判断

根据用户输入自动选择模式：

- **用户提供了论文标识**（arXiv URL、DOI、标题、本地 PDF 路径）→ 进入**阅读模式**
- **用户未提供论文标识**（如 "搜索最新的 LLM 论文"、"今天有什么好论文"）→ 进入**搜索模式**
- **用户提供了关键词**（如 "搜索 retrieval augmented generation"）→ 进入**搜索模式（Focus）**

---

# 搜索模式

## 步骤1：配置加载

加载研究兴趣配置文件，确定搜索方向。

### 配置文件路径解析（按优先级）

1. **用户在对话中显式指定路径** → 直接使用
2. **环境变量** `OBSIDIAN_VAULT_PATH` → 拼接 `$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml`
3. **均不可用** → 脚本使用内置默认配置（通用 AI/ML 领域）

```bash
# 解析环境变量（Claude Code bash 不自动 source shell profile）
if [ -z "$OBSIDIAN_VAULT_PATH" ]; then
    [ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc" 2>/dev/null || true
    [ -f "$HOME/.bash_profile" ] && source "$HOME/.bash_profile" 2>/dev/null || true
fi

CONFIG_PATH="$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml"
```

### 配置文件结构

配置文件为 YAML 格式，示例：

```yaml
# 语言设置（zh / en）
language: "zh"

# 研究领域定义
research_domains:
  大模型:
    keywords:
      - "pre-training"
      - "foundation model"
      - "large language model"
      - "LLM"
      - "transformer"
      - "model architecture"
    arxiv_categories: ["cs.AI", "cs.LG", "cs.CL"]
    priority: 5

  多模态:
    keywords:
      - "multimodal"
      - "vision-language"
      - "image-text"
      - "CLIP"
      - "visual grounding"
    arxiv_categories: ["cs.CV", "cs.MM", "cs.CL"]
    priority: 4

  智能体:
    keywords:
      - "agent"
      - "tool use"
      - "planning"
      - "reasoning"
      - "multi-agent"
    arxiv_categories: ["cs.AI", "cs.MA", "cs.RO"]
    priority: 3

# 排除关键词（包含这些词的论文将被过滤）
excluded_keywords:
  - "3D"
  - "review"
  - "workshop"
  - "survey"

# Semantic Scholar API Key（可选，提高请求限额）
semantic_scholar_api_key: null
```

**字段说明**：
- `research_domains`: 研究领域字典，每个领域包含：
  - `keywords`: 搜索和匹配用的关键词列表
  - `arxiv_categories`: 对应的 arXiv 分类列表
  - `priority`: 优先级（数值越高越优先）
- `excluded_keywords`: 排除关键词——标题或摘要中包含这些词的论文将被过滤掉
- `semantic_scholar_api_key`: 可选的 Semantic Scholar API key，配置后可提高请求限额

## 步骤2：论文搜索

使用 `scripts/search_arxiv.py` 脚本执行搜索。

### 2.1 普通模式（按兴趣域搜索）

当用户未指定 focus 关键词时，按配置文件中的兴趣域搜索：

```bash
cd "$SKILL_DIR"
python scripts/search_arxiv.py \
  --config "$CONFIG_PATH" \
  --output arxiv_filtered.json \
  --max-results 200 \
  --top-n 10 \
  --categories "cs.AI,cs.LG,cs.CL,cs.CV,cs.MM,cs.MA,cs.RO"
```

搜索流程：
1. **arXiv API 搜索**：搜索最近 30 天内指定分类的论文（最多 200 篇）
2. **Semantic Scholar 热门论文检索**：搜索过去一年的高影响力论文（按 influentialCitationCount 排序）
3. **合并、去重、评分、排序**：输出 top N 篇推荐论文

### 2.2 Focus 模式（按关键词搜索）

当用户指定了关注关键词时，以关键词搜索为主导：

```bash
cd "$SKILL_DIR"
python scripts/search_arxiv.py \
  --config "$CONFIG_PATH" \
  --output arxiv_filtered.json \
  --max-results 200 \
  --top-n 10 \
  --focus "retrieval augmented generation,RAG"
```

Focus 模式下：
- arXiv 搜索在标题和摘要中匹配 focus 关键词
- 相关性评分以 focus 关键词匹配为主导（标题匹配 +2.0，摘要匹配 +1.0）
- 原有兴趣域匹配仅作为 0.3 权重的辅助加分
- Semantic Scholar 也按 focus 关键词搜索

### 2.3 搜索参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 研究兴趣配置文件路径 | 由 `OBSIDIAN_VAULT_PATH` 推导 |
| `--output` | 输出 JSON 文件路径 | `arxiv_filtered.json` |
| `--max-results` | arXiv API 最大结果数 | 200 |
| `--top-n` | 最终输出的论文数 | 10 |
| `--categories` | arXiv 分类（逗号分隔） | `cs.AI,cs.LG,cs.CL,cs.CV,cs.MM,cs.MA,cs.RO` |
| `--target-date` | 基准日期（YYYY-MM-DD） | 当天日期 |
| `--focus` | Focus 关键词（逗号分隔） | 空（使用普通模式） |
| `--days` | 最近搜索窗口天数 | 30 |
| `--skip-hot-papers` | 跳过 Semantic Scholar 热门论文搜索 | 不跳过 |

## 步骤3：读取和展示结果

搜索完成后，读取 `arxiv_filtered.json` 并向用户展示结果：

```bash
cat arxiv_filtered.json
```

**JSON 结构**：
```json
{
  "target_date": "2026-05-08",
  "date_windows": {
    "recent_30d": { "start": "2026-04-08", "end": "2026-05-08" },
    "past_year": { "start": "2025-05-08", "end": "2025-04-07" }
  },
  "total_recent": 150,
  "total_hot": 30,
  "total_unique": 120,
  "top_papers": [
    {
      "arxiv_id": "2605.01234",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "affiliations": ["MIT", "Google"],
      "summary": "Abstract text...",
      "published": "2026-05-01T00:00:00Z",
      "categories": ["cs.AI", "cs.CL"],
      "pdf_url": "https://arxiv.org/pdf/2605.01234",
      "url": "https://arxiv.org/abs/2605.01234",
      "source": "arxiv",
      "is_hot_paper": false,
      "note_filename": "Paper_Title",
      "scores": {
        "relevance": 2.5,
        "recency": 3.0,
        "popularity": 1.5,
        "quality": 2.0,
        "recommendation": 7.83
      },
      "matched_domain": "大模型",
      "matched_keywords": ["LLM", "transformer"]
    }
  ]
}
```

**向用户展示时**：
- 按推荐评分从高到低排列
- 每篇论文显示：标题、评分、匹配领域、arXiv 链接
- 如果用户想深入某篇论文，可以直接给出 URL 进入阅读模式

## 评分体系

### 综合推荐评分

综合多个维度评分，归一化到 0-10 分：

```
推荐评分 = 相关性(40%) + 新近性(20%) + 热门度(30%) + 质量(10%)
```

**高影响力论文（来自 Semantic Scholar）使用调整权重**：

```
推荐评分 = 相关性(35%) + 新近性(10%) + 热门度(45%) + 质量(10%)
```

### 评分维度详情

#### 1. 相关性评分（满分 3.0）

与研究兴趣的匹配程度：
- 标题关键词匹配：每个 +0.5 分
- 摘要关键词匹配：每个 +0.3 分
- 类别匹配：+1.0 分

**Focus 模式下**：
- Focus 关键词标题匹配：+2.0 分
- Focus 关键词摘要匹配：+1.0 分
- 原有兴趣域匹配作为 0.3 权重辅助加分

#### 2. 新近性评分（满分 3.0）

- 最近 30 天内：+3.0 分
- 30-90 天内：+2.0 分
- 90-180 天内：+1.0 分
- 180 天以上：0 分

#### 3. 热门度评分（满分 3.0）

**高影响力论文**（Semantic Scholar）：
- 按 influentialCitationCount 归一化（100 次高影响力引用 = 满分）

**普通论文**（arXiv，无引用数据）：
- 最近 7 天：2.0（潜在热度）
- 7-14 天：1.5
- 14-30 天：1.0
- 30 天以上：0.5

#### 4. 质量评分（满分 3.0）

从摘要文本推断：
- 强创新指标（SOTA、breakthrough、first）：+0.7~1.0
- 方法指标（framework、architecture、algorithm）：+0.5
- 量化结果（outperforms、improves by）：+0.8
- 实验指标（benchmark、ablation）：+0.4

---

# 阅读模式

当用户提供论文标识（arXiv URL、DOI、标题、本地 PDF 路径）时，进入深度阅读模式。

本模式采用 **TeX 源码优先策略**：优先获取并使用 TeX 源码进行深度分析，仅在 TeX 不可用时回退到 PDF。

## 环境检查

在开始流水线前，检查运行环境：

### Python 版本检查

DeepPaperNote 脚本需要 Python >=3.10。检查并使用兼容的解释器：

```bash
# 检查默认 python3 版本
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    # 尝试查找兼容的解释器
    for py in python3.12 python3.11 python3.10 /opt/anaconda3/bin/python3; do
        if command -v $py &>/dev/null; then
            PY_EXEC=$py
            break
        fi
    done
    
    if [ -z "$PY_EXEC" ]; then
        echo "错误：需要 Python >=3.10，当前版本为 $PYTHON_VERSION"
        exit 1
    fi
else
    PY_EXEC=python3
fi
```

### Zotero 可用性检查

检查 Zotero MCP 工具是否可用（用于本地库搜索和 PDF 附件定位）：

```bash
# 尝试调用 Zotero MCP 工具
# 如果成功则标记 Zotero 可用，失败则记录"Zotero not available"并继续
```

## 完整流水线（12 步）

### 步骤 1：解析论文身份

将用户输入（URL、DOI、标题、arXiv ID、本地 PDF）解析为规范的论文身份。

**Zotero 优先策略**：
- 若 Zotero 可用，首先在本地库中搜索（按标题、DOI 或 arXiv ID）
- 若找到，使用 Zotero 的元数据作为规范身份（避免标题歧义）
- 若未找到，回退到网络 API（arXiv、Semantic Scholar、DOI）

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/resolve_paper.py \
  --input "<用户输入>" \
  --output /tmp/paper_resolved.json
```

**输出**：`/tmp/paper_resolved.json`，包含：
- `paper_id`: 规范 ID（如 `arxiv:2601.07372`）
- `title`: 论文标题
- `arxiv_id`: arXiv ID（如有）
- `doi`: DOI（如有）
- `source`: 来源（zotero / arxiv / doi / semantic_scholar）

### 步骤 2：收集元数据

从多个来源收集完整的论文元数据（作者、摘要、发表日期、引用数等）。

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/collect_metadata.py \
  --input /tmp/paper_resolved.json \
  --output /tmp/paper_metadata.json
```

**输出**：`/tmp/paper_metadata.json`，包含：
- `authors`: 作者列表
- `abstract`: 摘要
- `published_date`: 发表日期
- `citations`: 引用数（如有）
- `venue`: 发表会议/期刊（如有）

### 步骤 3：获取 TeX 源码（优先）或 PDF（fallback）

**TeX 优先策略**：
1. 若论文来自 arXiv，首先尝试获取 TeX 源码（`https://arxiv.org/src/{arxiv_id}`）
2. 若 TeX 源码可用，下载并解压到 `/tmp/paper_tex/{arxiv_id}/`
3. 若 TeX 源码不可用（约 20-30% 的 arXiv 论文），回退到 PDF

**PDF fallback 触发条件**：
- arXiv 不提供 TeX 源码（仅 PDF）
- 论文来自非 arXiv 来源（会议、期刊、预印本）
- TeX 源码下载失败

**TeX 源码获取**：
```bash
# 规范化 URL（从 /abs/ 转为 /src/）
ARXIV_ID=$(echo "$ARXIV_URL" | grep -oE '[0-9]{4}\.[0-9]{4,5}')
TEX_URL="https://arxiv.org/src/$ARXIV_ID"

# 下载 TeX 源码
mkdir -p /tmp/paper_tex/$ARXIV_ID
curl -L "$TEX_URL" -o /tmp/paper_tex/$ARXIV_ID.tar.gz

# 解压
cd /tmp/paper_tex/$ARXIV_ID && tar -xzf ../$ARXIV_ID.tar.gz

# 定位入口文件（main.tex、paper.tex 等）
MAIN_TEX=$(find . -maxdepth 1 -name "*.tex" | head -1)
```

**PDF fallback**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/fetch_pdf.py \
  --input /tmp/paper_metadata.json \
  --output /tmp/paper_pdf.json
```

**Zotero 本地 PDF 优先**：
- 若 Zotero 找到论文且有本地附件，使用 `locate_zotero_attachment.py` 定位本地 PDF
- 否则从网络下载（arXiv、DOI、Semantic Scholar）

**输出**：
- TeX 模式：`/tmp/paper_tex/{arxiv_id}/` 目录，包含所有 `.tex` 文件
- PDF 模式：`/tmp/paper_pdf.json`，包含 `pdf_path` 字段

### 步骤 4：提取证据（TeX 或 PDF）

**TeX 模式**：
1. 读取入口 `.tex` 文件
2. 递归遍历所有 `\input{}` 和 `\include{}` 引用的文件
3. 提取章节结构（`\section`、`\subsection`）
4. 提取关键内容：
   - 摘要（`\begin{abstract}`）
   - 方法描述（Introduction、Method 章节）
   - 实验结果（Results、Experiments 章节）
   - 公式（`\begin{equation}`、`$$...$$`）
   - 图表引用（`\ref{fig:...}`、`\ref{tab:...}`）

**PDF 模式**（fallback）：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/extract_evidence.py \
  --input /tmp/paper_pdf.json \
  --output /tmp/paper_evidence.json
```

从 PDF 提取结构化证据：
- `sections`: 章节列表（标题 + 文本）
- `candidate_chunks`: 候选文本块（按语义分割）
- `captions`: 图表标题
- `metrics`: 数值指标（表格中的性能数据）
- `equations`: 公式（OCR 提取）

**输出**：`/tmp/paper_evidence.json`（证据包）

### 步骤 5：提取图片资源

**TeX 模式**：
1. 扫描 TeX 源码中的图片引用（`\includegraphics{...}`）
2. 在源码目录中查找对应的图片文件（`.png`、`.pdf`、`.jpg`）
3. 复制图片到 `/tmp/paper_assets/{arxiv_id}/`

**PDF 模式**（fallback）：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/extract_pdf_assets.py \
  --input /tmp/paper_pdf.json \
  --output /tmp/paper_assets.json
```

从 PDF 提取嵌入的图片：
- 使用 PyMuPDF (fitz) 提取所有图片
- 按页码和位置命名（`page_3_img_1.png`）
- 保存到 `/tmp/paper_assets/{paper_id}/`

**输出**：`/tmp/paper_assets.json`，包含 `assets` 列表（图片路径）

### 步骤 6：规划图表放置

使用 placeholder-first 策略规划图表在笔记中的位置。

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/plan_figures.py \
  --evidence /tmp/paper_evidence.json \
  --assets /tmp/paper_assets.json \
  --output /tmp/figure_plan.json
```

**策略**：
1. 为每个图表创建占位符（`![[placeholder_fig_1]]`）
2. 根据 caption 和上下文匹配图片
3. 高置信度匹配（>0.8）：直接替换占位符为真实图片路径
4. 低置信度匹配：保留占位符，附加候选图片列表供人工选择

**输出**：`/tmp/figure_plan.json`，包含：
- `placeholders`: 占位符列表
- `high_confidence_matches`: 高置信度匹配（自动替换）
- `low_confidence_matches`: 低置信度匹配（需人工确认）

### 步骤 7：构建 synthesis bundle

将所有收集的数据整合为一个 JSON bundle，供 Claude 模型理解和写作。

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/build_synthesis_bundle.py \
  --metadata /tmp/paper_metadata.json \
  --evidence /tmp/paper_evidence.json \
  --assets /tmp/paper_assets.json \
  --figures /tmp/figure_plan.json \
  --output /tmp/synthesis_bundle.json
```

**输出**：`/tmp/synthesis_bundle.json`，包含：
- `metadata`: 论文元数据
- `evidence`: 结构化证据
- `assets`: 图片资源列表
- `figure_plan`: 图表放置计划
- `source_type`: "tex" 或 "pdf"（标识使用的源类型）

### 步骤 8：模型规划笔记（Claude）

**Model-first 原则**：Claude 负责理解论文和规划笔记结构，脚本仅负责数据收集。

读取 synthesis bundle 并创建笔记规划：

```bash
# Claude 读取 bundle
cat /tmp/synthesis_bundle.json
```

**规划内容**：
1. 笔记结构（章节划分）
2. 每个章节的核心内容（从 evidence 中提取）
3. 图表放置位置（使用 figure_plan）
4. 关键引用和公式
5. 与项目的关联（如用户指定了 project-path）

**输出**：在内存中创建 `note_plan`（不写入文件）

### 步骤 9：模型写作笔记（Claude）

根据 synthesis bundle 和 note_plan 写作完整的 Obsidian 笔记。

**笔记结构**：
```markdown
---
title: "论文标题"
authors: ["作者1", "作者2"]
year: 2024
venue: "会议/期刊"
arxiv_id: "2601.07372"
tags: ["tag1", "tag2"]
source_type: "tex"  # 或 "pdf"
---

# 论文标题

## 核心贡献

[从 evidence 中提取的核心贡献]

## 方法

[方法描述，包含公式和图表]

![[figure_1.png]]
*图 1：方法架构*

## 实验结果

[实验结果，包含表格和图表]

## 与项目的关联

[如果用户指定了 project-path，分析论文与项目的关联]

## 参考文献

- [论文链接](https://arxiv.org/abs/2601.07372)
```

**写作原则**：
- 深度分析而非浅层摘要
- 证据驱动（引用 evidence 中的具体内容）
- 图文并茂（使用 figure_plan 放置图片）
- 结构化（清晰的章节划分）
- 可操作（如有 project-path，提供具体的应用建议）

**输出**：写入 `/tmp/paper_note_draft.md`

### 步骤 10：Lint 校验

使用 style gate 校验笔记质量，确保符合 Obsidian 规范。

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/lint_note.py \
  --input /tmp/paper_note_draft.md \
  --output /tmp/lint_report.json
```

**校验项**：
1. Frontmatter 完整性（必需字段：title、authors、year）
2. Wikilink 格式（`[[path]]` 或 `[[path|alias]]`）
3. 图片嵌入格式（`![[image.png]]`）
4. 标题层级（不跳级，如 `##` 后不能直接 `####`）
5. 代码块闭合（` ``` ` 成对出现）
6. 公式格式（`$...$` 或 `$$...$$`）

**修复循环**：
- 若 lint 失败，Claude 根据 lint_report 修复问题
- 重新运行 lint 直到通过（最多 3 次）
- 若 3 次后仍失败，标记问题并继续（不阻塞流水线）

**输出**：`/tmp/lint_report.json`，包含：
- `passed`: 是否通过
- `errors`: 错误列表
- `warnings`: 警告列表

### 步骤 11：最终可读性审查（Claude）

Claude 进行最终的语言润色和可读性审查。

**审查内容**：
1. 语言流畅性（消除机器翻译痕迹）
2. 逻辑连贯性（章节间过渡自然）
3. 术语一致性（同一概念使用统一术语）
4. 格式美观性（列表、表格、代码块格式统一）

**输出**：更新 `/tmp/paper_note_draft.md`

### 步骤 12：保存到 Obsidian

将最终笔记保存到 Obsidian vault。

**调用脚本**：
```bash
cd "$SKILL_DIR" && $PY_EXEC scripts/write_obsidian_note.py \
  --input /tmp/paper_note_draft.md \
  --metadata /tmp/paper_metadata.json \
  --vault "$OBSIDIAN_VAULT_PATH" \
  --output /tmp/save_result.json
```

**保存路径**：
- 默认：`$OBSIDIAN_VAULT_PATH/20_Research/Papers/{year}/{arxiv_id}.md`
- 若文件已存在，生成新文件名（`{arxiv_id}_v2.md`）

**图片资源复制**：
- 将 `/tmp/paper_assets/{paper_id}/` 中的图片复制到 `$OBSIDIAN_VAULT_PATH/99_Attachments/Papers/{arxiv_id}/`
- 更新笔记中的图片路径为相对路径

**输出**：`/tmp/save_result.json`，包含：
- `note_path`: 笔记保存路径
- `assets_copied`: 复制的图片数量
- `status`: "success" 或 "error"

## TeX Fallback 说明

当 PDF 不可用或用户明确要求时，使用 TeX 源码阅读模式。

**触发条件**：
- 用户明确说"我要看 LaTeX 源码"或"下载 TeX 文件"
- PDF 无法获取但 arXiv 提供 TeX 源码（极少数情况）

**TeX 模式优势**：
- 纯文本，易于解析和理解
- 包含完整的公式和图表引用
- 可以查看 LaTeX 代码（用于复现实验、理解公式推导）

**TeX 模式劣势**：
- 不总是可用（约 20-30% 的 arXiv 论文不提供源码）
- 图片需要额外下载和路径解析
- 非 arXiv 来源不提供 TeX 源码

**使用 TeX 模式时**：
- 明确告知用户使用了 TeX 源码
- 在笔记 frontmatter 中标记 `source_type: "tex"`
- 图片提取从 TeX 源码目录中查找

---

# 脚本说明

## 搜索相关脚本

### search_arxiv.py

位于 `scripts/search_arxiv.py`，arXiv + Semantic Scholar 混合架构论文搜索脚本。

**功能**：
1. **arXiv API 搜索**：按分类或关键词调用 arXiv API，获取论文并解析 XML
2. **Semantic Scholar 热门论文检索**：搜索高影响力论文（按 influentialCitationCount）
3. **多维评分**：计算相关性、新近性、热门度、质量四维评分
4. **合并去重排序**：去重、排序、输出 top N 论文到 JSON

**CLI 接口**：
```bash
python scripts/search_arxiv.py \
  --config <配置文件路径> \
  --output <输出JSON路径> \
  --max-results <最大结果数> \
  --top-n <输出论文数> \
  --categories <分类列表> \
  --target-date <YYYY-MM-DD> \
  --focus <关键词列表> \
  --days <搜索天数> \
  --skip-hot-papers
```

### scan_existing_notes.py

位于 `scripts/scan_existing_notes.py`，扫描 Obsidian vault 笔记构建关键词索引。

**功能**：
1. 扫描 `20_Research/Papers/` 目录下所有 `.md` 文件
2. 提取 frontmatter（title、tags）
3. 从标题提取关键词（缩写、专有名词、技术术语）
4. 构建关键词到笔记路径的映射表

**CLI 接口**：
```bash
python scripts/scan_existing_notes.py \
  --vault <Obsidian vault 路径> \
  --output <输出JSON路径> \
  --papers-dir <Papers相对路径>
```

### link_keywords.py

位于 `scripts/link_keywords.py`，在 Markdown 文本中自动将关键词替换为 wikilink。

**功能**：
1. 读取笔记索引 JSON
2. 在文本中查找关键词并替换为 `[[path|keyword]]` 格式
3. 保护 frontmatter、标题行、代码块、已有 wikilink 不被修改
4. 按关键词长度降序匹配，避免部分匹配

**CLI 接口**：
```bash
python scripts/link_keywords.py \
  --index <关键词索引JSON> \
  --input <输入Markdown文件> \
  --output <输出Markdown文件>
```

### common_words.py

位于 `scripts/common_words.py`，通用词过滤集合，被 `scan_existing_notes.py` 和 `link_keywords.py` 共享。包含应在关键词提取和自动链接中排除的通用词（如 and, for, model, learning 等）。

## 深度阅读流水线脚本（DeepPaperNote）

以下脚本从 DeepPaperNote 项目复制而来，用于完整的深度阅读流水线。

### common.py

位于 `scripts/common.py`，共享工具函数库。

**功能**：
- 命令行参数解析（`base_parser`）
- JSON 读写（`emit`、`maybe_load_json_record`）
- 论文身份解析（`resolve_reference`、`paper_id_for_record`）
- 文件路径处理
- 日期时间工具

### contracts.py

位于 `scripts/contracts.py`，数据契约定义。

**功能**：
- 定义流水线各阶段的数据结构
- `empty_evidence_pack`: 空证据包模板
- 类型注解和验证

### resolve_paper.py

位于 `scripts/resolve_paper.py`，论文身份解析。

**功能**：
- 解析用户输入（URL、DOI、标题、arXiv ID、本地 PDF）
- 规范化为统一的论文身份
- 支持 Zotero 本地库搜索

**CLI 接口**：
```bash
python scripts/resolve_paper.py \
  --input "<用户输入>" \
  --output <输出JSON路径> \
  --paper-id <可选的自定义ID>
```

### collect_metadata.py

位于 `scripts/collect_metadata.py`，元数据收集。

**功能**：
- 从多个来源收集论文元数据（arXiv、Semantic Scholar、DOI）
- 合并和去重元数据
- 提取作者、摘要、发表日期、引用数等

**CLI 接口**：
```bash
python scripts/collect_metadata.py \
  --input <resolved论文JSON> \
  --output <输出JSON路径>
```

### fetch_pdf.py

位于 `scripts/fetch_pdf.py`，PDF 获取（fallback）。

**功能**：
- 从多个来源下载 PDF（arXiv、DOI、Semantic Scholar）
- 支持 Zotero 本地附件定位
- 验证 PDF 完整性

**CLI 接口**：
```bash
python scripts/fetch_pdf.py \
  --input <metadata论文JSON> \
  --output <输出JSON路径> \
  --download-dir <PDF下载目录>
```

### extract_evidence.py

位于 `scripts/extract_evidence.py`，证据提取（PDF 模式）。

**功能**：
- 从 PDF 提取结构化证据
- 章节分割（sections）
- 候选文本块（candidate_chunks）
- 图表标题（captions）
- 数值指标（metrics）
- 公式提取（equations）

**CLI 接口**：
```bash
python scripts/extract_evidence.py \
  --input <PDF论文JSON> \
  --output <输出JSON路径>
```

### extract_pdf_assets.py

位于 `scripts/extract_pdf_assets.py`，PDF 图片提取（fallback）。

**功能**：
- 使用 PyMuPDF (fitz) 提取 PDF 中的图片
- 按页码和位置命名
- 保存到指定目录

**CLI 接口**：
```bash
python scripts/extract_pdf_assets.py \
  --input <PDF论文JSON> \
  --output <输出JSON路径> \
  --assets-dir <图片保存目录>
```

### plan_figures.py

位于 `scripts/plan_figures.py`，图表放置规划。

**功能**：
- Placeholder-first 策略
- 根据 caption 和上下文匹配图片
- 高置信度匹配自动替换
- 低置信度匹配保留占位符

**CLI 接口**：
```bash
python scripts/plan_figures.py \
  --evidence <证据JSON> \
  --assets <图片资源JSON> \
  --output <输出JSON路径>
```

### build_synthesis_bundle.py

位于 `scripts/build_synthesis_bundle.py`，构建 synthesis bundle。

**功能**：
- 整合所有收集的数据为一个 JSON bundle
- 供 Claude 模型理解和写作
- 包含 metadata、evidence、assets、figure_plan

**CLI 接口**：
```bash
python scripts/build_synthesis_bundle.py \
  --metadata <元数据JSON> \
  --evidence <证据JSON> \
  --assets <图片资源JSON> \
  --figures <图表规划JSON> \
  --output <输出JSON路径>
```

### lint_note.py

位于 `scripts/lint_note.py`，笔记校验。

**功能**：
- Style gate 校验
- Frontmatter 完整性
- Wikilink 格式
- 图片嵌入格式
- 标题层级
- 代码块闭合
- 公式格式

**CLI 接口**：
```bash
python scripts/lint_note.py \
  --input <笔记Markdown文件> \
  --output <lint报告JSON>
```

### write_obsidian_note.py

位于 `scripts/write_obsidian_note.py`，保存到 Obsidian。

**功能**：
- 保存笔记到 Obsidian vault
- 复制图片资源到 Attachments 目录
- 更新图片路径为相对路径
- 处理文件名冲突

**CLI 接口**：
```bash
python scripts/write_obsidian_note.py \
  --input <笔记Markdown文件> \
  --metadata <元数据JSON> \
  --vault <Obsidian vault路径> \
  --output <保存结果JSON>
```

### run_pipeline.py

位于 `scripts/run_pipeline.py`，流水线执行器。

**功能**：
- 按顺序执行完整的 12 步流水线
- 步骤失败处理（重试、fallback、停止）
- 中间结果缓存

**CLI 接口**：
```bash
python scripts/run_pipeline.py \
  --input "<用户输入>" \
  --vault <Obsidian vault路径> \
  --output <最终结果JSON>
```

### locate_zotero_attachment.py

位于 `scripts/locate_zotero_attachment.py`，Zotero 附件定位。

**功能**：
- 在 Zotero storage/ 目录中定位本地 PDF 附件
- 支持多种 Zotero 安装路径

**CLI 接口**：
```bash
python scripts/locate_zotero_attachment.py \
  --item-key <Zotero item key> \
  --output <输出JSON路径>
```

### create_input_record.py

位于 `scripts/create_input_record.py`，创建输入记录。

**功能**：
- 将用户输入规范化为标准输入记录
- 用于流水线的起点

**CLI 接口**：
```bash
python scripts/create_input_record.py \
  --input "<用户输入>" \
  --output <输出JSON路径>
```

### check_environment.py

位于 `scripts/check_environment.py`，环境检查。

**功能**：
- 检查 Python 版本（>=3.10）
- 检查依赖包（PyMuPDF、pypdf、pdfplumber）
- 检查 Zotero 可用性
- 检查 Obsidian vault 路径

**CLI 接口**：
```bash
python scripts/check_environment.py \
  --vault <Obsidian vault路径> \
  --output <检查结果JSON>
```

### materialize_figure_asset.py

位于 `scripts/materialize_figure_asset.py`，图片资源具化。

**功能**：
- 将占位符替换为真实图片路径
- 处理高置信度匹配
- 生成最终的图片嵌入代码

**CLI 接口**：
```bash
python scripts/materialize_figure_asset.py \
  --plan <图表规划JSON> \
  --output <输出JSON路径>
```

---

# 依赖项

## 搜索模式依赖

- **Python 3.x**（运行搜索和筛选脚本）
- **PyYAML**（解析研究兴趣配置文件）
  ```bash
  pip install pyyaml
  ```
- **requests**（可选，用于 Semantic Scholar API；若未安装则回退到 urllib）
  ```bash
  pip install requests
  ```
- **网络连接**（访问 arXiv API 和 Semantic Scholar API）

## 阅读模式依赖

- **Python >=3.10**（DeepPaperNote 脚本要求）
- **PyMuPDF (fitz)**（PDF 处理，fallback 模式）
  ```bash
  pip install pymupdf
  ```
- **pypdf**（PDF 元数据提取）
  ```bash
  pip install pypdf
  ```
- **pdfplumber**（PDF 表格提取）
  ```bash
  pip install pdfplumber
  ```
- **Zotero**（可选，用于本地库集成和 PDF 附件定位）
- **Zotero MCP 工具**（可选，用于 Zotero 集成）

## 环境变量

- **OBSIDIAN_VAULT_PATH**：Obsidian vault 路径（搜索和阅读模式共享）
  ```bash
  export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
  ```

## 配置文件

- **研究兴趣配置**：`$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml`（搜索模式使用）
