## ADDED Requirements

### Requirement: HF Daily Papers 搜索

系统 SHALL 在搜索模式中集成 Hugging Face Daily Papers API，作为第三搜索源获取社区热门 AI 论文。

#### Scenario: 正常 HF Daily Papers 搜索
- **WHEN** 搜索模式执行且配置中包含 AI/ML 相关领域
- **THEN** 系统调用 `GET https://huggingface.co/api/daily_papers` 获取最近 Daily Papers
- **AND** 将结果与 arXiv + Semantic Scholar 结果去重合并

#### Scenario: HF API 不可用
- **WHEN** HF Daily Papers API 返回错误或超时
- **THEN** 系统跳过 HF 搜索，继续使用 arXiv + Semantic Scholar 结果
- **AND** 记录警告信息（不阻塞流水线）

### Requirement: HF Papers 语义搜索

系统 SHALL 支持通过 HF Papers Search API 进行语义和全文搜索。

#### Scenario: Focus 模式 HF 语义搜索
- **WHEN** 用户使用 Focus 模式指定关键词
- **THEN** 系统调用 `GET https://huggingface.co/api/papers/search?q={keywords}&limit=20` 补充搜索
- **AND** HF 搜索结果与 arXiv/Semantic Scholar 结果去重合并

#### Scenario: HF 搜索无结果
- **WHEN** HF Search API 返回空结果
- **THEN** 系统优雅降级，仅使用 arXiv/Semantic Scholar 结果

### Requirement: HF 热门度评分加分

系统 SHALL 为出现在 HF Daily Papers 中的论文增加热门度评分加分。

#### Scenario: 论文在 HF Daily Papers 中
- **WHEN** 论文出现在 HF Daily Papers 结果中
- **THEN** 热门度评分增加 +0.5 分（社区热度标记）
- **AND** 在结果中标记 HF 热门来源

#### Scenario: 论文有 HF 关联资源
- **WHEN** 论文在 HF 上有关联的 models/datasets/spaces
- **THEN** 质量评分增加 +0.3 分（生态实现度标记）

### Requirement: HF URL 和 arXiv ID 解析

系统 SHALL 识别 Hugging Face 论文页面 URL 并解析为 arXiv ID。

#### Scenario: 用户提供 HF 论文 URL
- **WHEN** 用户输入包含 `huggingface.co/papers/` 或 `hf.co/papers/`
- **THEN** 系统提取 arXiv ID（如 `2602.08025`）
- **AND** 进入阅读模式

#### Scenario: 用户提供 HF markdown URL
- **WHEN** 用户输入包含 `huggingface.co/papers/{ID}.md`
- **THEN** 系统提取 arXiv ID 并进入阅读模式