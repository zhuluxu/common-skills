## MODIFIED Requirements

### Requirement: arXiv URL 解析增加 HF fallback

系统 SHALL 在 `resolve_reference` 的 `arxiv_url` 分支中，arXiv API 返回空结果时增加 HF Papers API fallback。

#### Scenario: arXiv API 限流时回退到 HF
- **WHEN** `resolve_reference` 识别输入为 `arxiv_url` 但 `safe_fetch_arxiv_entries` 返回空列表（因限流）
- **THEN** 系统尝试 HF Papers API 获取元数据（`GET https://huggingface.co/api/papers/{arxiv_id}`）
- **AND** 若 HF 返回数据，使用 HF 元数据填充 resolved record（source_type: `hf_paper_url`）

#### Scenario: arXiv 和 HF 均不可用
- **WHEN** arXiv API 限流且 HF API 也无数据
- **THEN** 系统回退到 title_query 方式（当前已有行为）
- **AND** 使用 arXiv ID 作为标题进行搜索

#### Scenario: arXiv API 正常
- **WHEN** `safe_fetch_arxiv_entries` 正常返回论文数据
- **THEN** 不调用 HF API（避免不必要的请求）