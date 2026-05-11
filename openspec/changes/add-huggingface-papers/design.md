## Context

paper-search-reader 已有 arXiv API + Semantic Scholar API 的双源搜索能力，以及 TeX 优先/PDF fallback 的阅读流水线。但缺少 Hugging Face Papers 这一 AI 论文生态的关键入口——HF Papers 提供 Daily Papers（社区投票热门论文）、语义搜索、论文 markdown 全文、以及论文关联的 models/datasets/spaces/GitHub 信息，这些都是现有搜索源无法提供的。

现状：
- 搜索模式仅支持 arXiv API（按分类/关键词搜索）和 Semantic Scholar（高影响力论文）
- 阅读模式的论文内容获取路径：TeX 源码 > PDF，没有 HTML/markdown 全文途径
- URL 解析仅支持 arXiv URL，不支持 `hf.co/papers/` 格式

约束：
- HF Papers 是只读集成（不需要写入操作如 claim authorship、update links）
- HF API 无需认证即可访问公开数据（Daily Papers、搜索、元数据）
- markdown 全文依赖 arXiv HTML 版本存在（约 70-80% 的 arXiv 论文有 HTML 版本）

## Goals / Non-Goals

**Goals:**
- 在搜索模式中新增 HF Daily Papers 作为第三搜索源，获取社区热门论文
- 在搜索模式中新增 HF Papers Search API 作为语义搜索补充
- 在阅读模式中新增 HF markdown 全文获取，优先级在 TeX 之后、PDF 之前
- 在阅读模式步骤2中新增 HF 元数据增强（关联 models/datasets/spaces/GitHub）
- 在模式判断中新增 HF URL 识别

**Non-Goals:**
- 不实现 HF 写入操作（claim authorship、index paper、update links）
- 不实现 HF 论文评论/投票功能的集成
- 不修改评分体系的核心权重（仅新增 HF 相关的加分项）
- 不创建新的 HF 专用脚本文件（所有逻辑扩展现有脚本）

## Decisions

### Decision 1: HF 搜索结果合并到现有评分体系

**选择**：将 HF Daily Papers 结果作为额外搜索源，合并到 arXiv + Semantic Scholar 结果池中统一评分排序。

**理由**：
- HF Daily Papers 与 arXiv 搜索有大量重叠（都来自 arXiv），去重后增量价值在社区热度和关联资源
- 统一评分体系让用户看到的是一份排序好的推荐列表，而非三份独立列表

**替代方案**：
- 三源并列展示（被拒：用户体验差，重复论文多）
- 仅 HF 搜索（被拒：覆盖面不如 arXiv API + Semantic Scholar 的组合）

### Decision 2: HF 获取优先级在搜索和阅读中的位置

**搜索模式优先级**：arXiv API → Semantic Scholar → HF Daily Papers → HF Search

**阅读模式内容获取优先级**：TeX 源码 → HF markdown 全文 → PDF

**理由**：
- TeX 源码包含最完整的信息（公式、图片引用、章节结构）
- HF markdown 是 arXiv HTML 的渲染版本，质量高于 PDF 文本提取，包含可读的公式和图表
- PDF 是最差的选择（需要 OCR，文本提取质量低）

**替代方案**：
- HF markdown 优先于 TeX（被拒：markdown 是 HTML 渲染，不如原始 TeX 完整）
- HF markdown 与 PDF 同优先级（被拒：markdown 质量明显优于 PDF 文本提取）

### Decision 3: 关联资源信息嵌入 Obsidian 笔记

**选择**：在阅读模式生成的笔记中新增 `## 关联资源` 章节，列出 HF 提供的 models/datasets/spaces/GitHub 链接。

**理由**：
- 关联资源是 HF 独特价值，对理解论文的实际应用至关重要
- 嵌入笔记中比单独输出更方便查阅

### Decision 4: 不创建新的 Python 脚本

**选择**：将 HF API 调用逻辑集成到现有脚本中（search_arxiv.py 新增 HF 搜索，resolve_paper.py 新增 HF URL 解析，collect_metadata.py 新增 HF 元数据合并）。

**理由**：
- HF API 调用是简单 HTTP 请求，不需要复杂的解析逻辑
- 保持脚本数量精简，避免项目膨胀
- 类比 DeepPaperNote 脚本的集成方式

**替代方案**：
- 创建独立的 search_huggingface.py（被拒：增加脚本数量，搜索合并逻辑需要额外编排）
- 创建独立的 hf_client.py 工具库（被拒：当前规模不需要客户端抽象层）

## Risks / Trade-offs

- **HF API 不可用或限流** → 已有 arXiv + Semantic Scholar 作为 fallback，HF 搜索失败不阻塞
- **HF markdown 依赖 arXiv HTML 版本** → 约 20-30% 的论文没有 HTML 版本，404 时 fallback 到 PDF
- **HF 论文覆盖率** → HF Papers 主要覆盖 AI/ML 领域，非 AI 论文需依赖 arXiv + Semantic Scholar
- **Daily Papers 时效性** → 论文只能在发表后 14 天内提交到 Daily Papers，较旧的论文需用搜索 API