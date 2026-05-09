## Why

当前 `paper-search-reader` 的阅读模式过于简单——仅下载 TeX 源码并生成简单摘要。用户需要一个完整的深度阅读流水线，能够：
1. 生成高质量的 Obsidian 笔记（结构化、证据驱动、图文并茂）
2. 支持多种论文来源（本地 PDF、Zotero、arXiv、DOI）
3. 提取并嵌入论文图片
4. 进行深度分析而非浅层摘要

DeepPaperNote 项目已实现了成熟的深度阅读流水线，但它：
- 只支持 PDF，不支持 TeX 源码
- 是独立项目，未与搜索能力整合

**关键技术决策：TeX vs PDF**

经过分析，**应该采用 PDF 优先策略**，原因：
1. **TeX 源码不总是可用**：arXiv 上约 20-30% 的论文不提供源码（仅 PDF）
2. **PDF 是通用格式**：所有论文都有 PDF，包括非 arXiv 来源（会议、期刊、预印本）
3. **图片提取**：PDF 可以直接提取嵌入的图片；TeX 需要额外下载图片文件且路径解析复杂
4. **成熟工具链**：PyMuPDF (fitz) 对 PDF 的文本和图片提取已非常成熟
5. **TeX 的优势有限**：虽然 TeX 是纯文本，但现代 PDF 提取工具已能很好地保留结构（sections、公式、表格）

**TeX 源码的保留场景**：
- 当用户明确需要查看 LaTeX 代码（如复现实验、理解公式推导）
- 作为 PDF 不可用时的 fallback（极少数情况）

## What Changes

- **整合 DeepPaperNote 流水线**：将完整的 12 步流水线整合到 `paper-search-reader` 的阅读模式
- **PDF 优先策略**：阅读模式默认获取 PDF 而非 TeX 源码
- **保留 TeX fallback**：当 PDF 不可用或用户明确要求时，回退到 TeX 源码阅读
- **复制 DeepPaperNote 脚本**：将 DeepPaperNote 的所有脚本复制到 paper-search-reader/scripts/ 目录
- **统一入口**：用户通过 `paper-search-reader` skill 即可完成"搜索 → 深度阅读 → 生成笔记"全流程
- **Zotero 集成**：支持从本地 Zotero 库优先获取论文和 PDF

## Capabilities

### New Capabilities
- `deep-reading-pipeline`: 完整的深度阅读流水线——resolve paper → collect metadata → fetch PDF → extract evidence → extract assets → plan figures → synthesis → model planning → model writing → lint → final review → save to Obsidian
- `pdf-evidence-extraction`: 从 PDF 提取结构化证据——sections、candidate chunks、captions、metrics、equations
- `figure-extraction-and-placement`: 从 PDF 提取图片并智能放置到笔记中——placeholder-first 策略，高置信度图片替换占位符
- `obsidian-note-generation`: 生成高质量 Obsidian 笔记——frontmatter、wikilinks、图片嵌入、公式渲染、深度分析
- `zotero-integration`: Zotero 本地库集成——优先从 Zotero 搜索论文、获取本地 PDF 附件

### Modified Capabilities
- `paper-search`: 搜索结果现在可以直接触发深度阅读流水线（用户选择某篇论文后自动进入阅读模式）

## Impact

- **`paper-search-reader/SKILL.md`**：阅读模式部分需要大幅重写，从简单的 TeX 下载改为完整的 DeepPaperNote 流水线
- **`paper-search-reader/scripts/`**：需要复制 DeepPaperNote 的 16 个脚本文件到此目录
- **新增 Python 依赖**：PyMuPDF (fitz)、pypdf、pdfplumber（PDF 处理）
- **Obsidian vault 配置**：需要用户配置 Obsidian vault 路径以保存笔记
- **向后兼容性**：保留 TeX 源码阅读作为 fallback，不破坏现有用户的工作流
