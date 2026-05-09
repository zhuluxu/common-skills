## Why

当前 `paper-search-reader/SKILL.md` 仅支持给定 arXiv URL 后下载并阅读单篇论文。用户需要一个完善的论文检索能力——能根据研究兴趣配置自动搜索 arXiv 和 Semantic Scholar，筛选、多维评分并排序论文，让用户快速发现高质量、高相关性的最新和热门论文。`evil-read-arxiv/start-my-day` 项目中已有成熟的搜索、筛选、评分实现，现在需要将这些能力整合到 `paper-search-reader` skill 中。

## What Changes

- **新增论文搜索能力**：在 SKILL.md 中新增"论文搜索"工作流，支持按分类/关键词搜索 arXiv 论文
- **新增 Semantic Scholar 热门论文检索**：整合 Semantic Scholar API，搜索过去一年高影响力论文
- **新增多维评分体系**：相关性(40%)、新近性(20%)、热门度(30%)、质量(10%) 综合评分
- **新增 Focus 模式**：支持用户指定今日关注关键词，搜索以 focus 关键词为主导
- **新增研究兴趣配置支持**：从 YAML 配置文件读取研究领域、关键词、分类和排除词
- **保留原有单篇阅读能力**：原有的 URL → 下载 → 阅读 → 生成报告流程保持不变
- **整合已有脚本**：`scripts/search_arxiv.py`、`scan_existing_notes.py`、`link_keywords.py`、`common_words.py` 已存在，需要在 SKILL.md 中正确引用

## Capabilities

### New Capabilities
- `paper-search`: 论文搜索与筛选能力——支持 arXiv API 搜索（按分类/按关键词）、Semantic Scholar 热门论文检索、多维评分体系、Focus 模式、研究兴趣配置驱动的自动筛选
- `search-result-output`: 搜索结果输出能力——将筛选后的论文列表以结构化 JSON 输出，包含评分、匹配领域、匹配关键词等信息，供后续消费

### Modified Capabilities
<!-- 无既有规范需要修改 -->

## Impact

- **`paper-search-reader/SKILL.md`**：主要修改目标，需要大幅重写以整合搜索能力
- **`paper-search-reader/scripts/`**：已有 4 个 Python 脚本，SKILL.md 需正确引用它们的 CLI 接口
- **外部依赖**：需要网络访问 arXiv API 和 Semantic Scholar API；需要 Python 3.x、PyYAML、可选 requests 库
- **配置文件**：需要用户提供 `research_interests.yaml` 配置文件（路径可通过参数或环境变量指定）
