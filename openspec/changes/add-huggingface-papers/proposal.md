## Why

paper-search-reader 的搜索模式仅支持 arXiv API 和 Semantic Scholar，缺少 Hugging Face Papers 这一 AI 论文领域的重要资源。HF Papers 提供：Daily Papers 热门论文、论文 markdown 全文、结构化元数据、关联的 models/datasets/spaces、GitHub 仓库链接——这些是 arXiv 和 Semantic Scholar 都无法提供的独特信息。阅读模式也缺少 HF markdown 全文作为 TeX/PDF 之外的第三种获取论文内容的途径。

## What Changes

- **新增 HF Papers 搜索能力**：在搜索模式中集成 HF Daily Papers API（热门论文）和 HF Papers Search API（语义搜索），作为 arXiv/Semantic Scholar 之外的第三搜索源
- **新增 HF Papers 元数据增强**：在阅读模式步骤1（resolve）和步骤2（collect metadata）中，调用 HF Papers API 获取关联资源（models/datasets/spaces/GitHub）
- **新增 HF markdown 全文获取**：在阅读模式步骤3-4 中，增加 HF markdown 作为优先于 PDF 的论文内容获取方式（优先级：TeX > HF markdown > PDF）
- **新增 HF 论文识别**：模式判断中识别 HF URL（`hf.co/papers/` 或 `huggingface.co/papers/`）

## Capabilities

### New Capabilities
- `huggingface-papers-search`: HF Papers 搜索——Daily Papers 热门论文获取、语义搜索、结果合并到现有评分体系
- `huggingface-papers-reading`: HF Papers 阅读增强——HF markdown 全文获取、结构化元数据（关联 models/datasets/spaces/GitHub）、HF URL 解析

### Modified Capabilities
- `paper-search`: 搜索模式新增 HF Papers 作为第三搜索源，结果合并到统一评分体系
- `deep-reading-pipeline`: 阅读模式步骤3（获取论文内容）新增 HF markdown 获取途径，优先级在 TeX 之后、PDF 之前

## Impact

- **SKILL.md**：搜索模式新增 HF 搜索流程和评分权重调整；阅读模式新增 HF markdown 获取路径和 URL 解析
- **scripts/search_arxiv.py**：新增 HF Daily Papers 和 Search API 调用逻辑
- **scripts/common.py**：新增 HF Paper ID 解析工具函数
- **scripts/resolve_paper.py**：新增 HF URL 识别和 HF API 查询
- **scripts/collect_metadata.py**：新增 HF 元数据合并（关联资源）
- **依赖**：新增 `requests`（HF API 调用，已有则无需新增）