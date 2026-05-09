## Context

当前 `paper-search-reader` 有两个模式：
1. **搜索模式**：已完善，使用 `search_arxiv.py` 搜索和评分论文
2. **阅读模式**：过于简单，仅下载 TeX 源码并生成简单摘要

DeepPaperNote 是一个独立的成熟项目，位于 `/Users/laylaq/PycharmProjects/DeepPaperNote/`，提供完整的深度阅读流水线。

**约束**：
- DeepPaperNote 的脚本已经完善且经过验证
- 应复制 DeepPaperNote 的脚本到 paper-search-reader 项目中
- paper-search-reader 是 Claude Code skill，通过 SKILL.md 描述工作流
- 复制后的脚本需要独立维护

## Goals / Non-Goals

**Goals:**
- 在 paper-search-reader 的阅读模式中整合 DeepPaperNote 完整流水线
- 采用 PDF 优先策略（TeX 作为 fallback）
- 复制 DeepPaperNote 脚本到 paper-search-reader/scripts/ 目录
- 支持"搜索 → 选择 → 深度阅读"的完整用户旅程
- 生成高质量 Obsidian 笔记（图文并茂、深度分析）

**Non-Goals:**
- 不修改 DeepPaperNote 项目本身
- 不移除 TeX 源码阅读能力（保留为 fallback）
- 不改变搜索模式的现有行为
- 不在复制后的脚本中保持与 DeepPaperNote 的同步（独立维护）

## Decisions

### 1. PDF 优先，TeX 作为 fallback

**选择**：阅读模式默认获取 PDF，仅在以下情况使用 TeX：
- PDF 不可用（极少数情况）
- 用户明确要求查看 LaTeX 源码

**理由**：
- **通用性**：所有论文都有 PDF，TeX 源码仅 arXiv 部分提供
- **图片提取**：PDF 可直接提取图片；TeX 需要额外处理图片文件路径
- **工具成熟度**：PyMuPDF 对 PDF 的处理已非常成熟
- **DeepPaperNote 兼容**：DeepPaperNote 只支持 PDF

**替代方案**：
- TeX 优先 → 拒绝，因为 TeX 不总是可用，且图片处理复杂
- 同时支持两种路径 → 拒绝，维护成本高且用户体验混乱

### 2. 复制 DeepPaperNote 脚本到本项目

**选择**：将 DeepPaperNote 的所有脚本复制到 `paper-search-reader/scripts/` 目录：
```bash
cp -r /Users/laylaq/PycharmProjects/DeepPaperNote/scripts/* \
      paper-search-reader/scripts/
```

**理由**：
- **独立部署**：paper-search-reader 可以独立使用，不依赖外部项目
- **版本控制**：复制后的脚本版本固定，不受 DeepPaperNote 更新影响
- **简化配置**：用户不需要配置 DEEPPAPERNOTE_DIR 环境变量
- **便于修改**：如需针对 paper-search-reader 的特定需求调整脚本，可以直接修改

**替代方案**：
- 引用 DeepPaperNote 脚本 → 用户明确拒绝，要求复制
- 作为 Python 包安装 → 过度工程化，DeepPaperNote 未发布为包

**复制清单**：
- `scripts/common.py` - 共享工具函数
- `scripts/contracts.py` - 数据契约定义
- `scripts/resolve_paper.py` - 论文身份解析
- `scripts/collect_metadata.py` - 元数据收集
- `scripts/fetch_pdf.py` - PDF 获取
- `scripts/extract_evidence.py` - 证据提取
- `scripts/extract_pdf_assets.py` - PDF 图片提取
- `scripts/plan_figures.py` - 图表规划
- `scripts/build_synthesis_bundle.py` - 构建 synthesis bundle
- `scripts/lint_note.py` - 笔记校验
- `scripts/write_obsidian_note.py` - 保存到 Obsidian
- `scripts/run_pipeline.py` - 流水线执行器
- `scripts/locate_zotero_attachment.py` - Zotero 附件定位
- `scripts/create_input_record.py` - 创建输入记录
- `scripts/check_environment.py` - 环境检查
- `scripts/materialize_figure_asset.py` - 图片资源具化

### 3. 工作流整合点

**选择**：在 SKILL.md 的阅读模式中，按以下顺序调用本地脚本：
1. 用户提供论文标识（URL、DOI、标题、arXiv ID）
2. 调用 `scripts/run_pipeline.py` 生成 synthesis bundle
3. Claude 读取 bundle 并生成笔记
4. 调用 `scripts/lint_note.py` 校验
5. 进行 final readability review
6. 调用 `scripts/write_obsidian_note.py` 保存

**理由**：
- 复用 DeepPaperNote 的完整流水线
- Claude 负责理解和写作（model-first 原则）
- 脚本负责数据收集和结构化

### 4. Obsidian vault 配置

**选择**：复用现有的 `OBSIDIAN_VAULT_PATH` 环境变量，与搜索模式保持一致。

**理由**：
- 用户已经为搜索模式配置了该变量
- 统一配置减少用户负担

## Risks / Trade-offs

- **[脚本维护成本]** → 复制后的脚本需要独立维护，DeepPaperNote 的更新不会自动同步；可通过定期手动同步缓解
- **[代码重复]** → 两个项目中存在相同的脚本代码；但换来了独立部署和版本稳定性
- **[Python 版本要求]** → 脚本需要 Python >=3.10；SKILL.md 中需要检查并使用兼容的解释器
- **[PDF 不可用]** → 少数情况下 PDF 无法获取；回退到 TeX 源码或明确告知用户
- **[图片提取失败]** → 使用 placeholder-first 策略，图片提取失败不影响笔记生成
- **[Zotero 未安装]** → 优雅降级，跳过 Zotero 集成，直接从网络获取
