## ADDED Requirements

### Requirement: 结构化 JSON 输出
系统 SHALL 将筛选后的论文列表以 JSON 格式输出到文件，包含完整的元数据和评分信息。

#### Scenario: 正常输出
- **WHEN** 搜索和评分完成后
- **THEN** 系统将结果写入 `arxiv_filtered.json`（或用户指定的输出路径），JSON 包含：target_date、date_windows、total_recent、total_hot、total_unique、top_papers 列表

#### Scenario: Top N 筛选
- **WHEN** 筛选完成后
- **THEN** 系统按综合推荐评分降序排列，输出前 N 篇论文（默认 10 篇，可通过 `--top-n` 配置）

### Requirement: 每篇论文包含完整信息
输出的每篇论文 SHALL 包含：论文 ID、标题、作者列表、机构、摘要、发布日期、分类、各维度评分、综合推荐评分、匹配的领域、匹配的关键词、来源标记（arXiv/semantic_scholar）、是否热门论文标记。

#### Scenario: arXiv 来源论文
- **WHEN** 论文来自 arXiv API
- **THEN** 包含 arxiv_id、title、authors、affiliations、summary、published、categories、pdf_url、url、scores、matched_domain、matched_keywords、source="arxiv"、note_filename

#### Scenario: Semantic Scholar 来源论文
- **WHEN** 论文来自 Semantic Scholar API
- **THEN** 包含 arxiv_id（从 externalIds 提取）、title、authors、affiliations、abstract、publicationDate、citationCount、influentialCitationCount、url、scores、matched_domain、matched_keywords、source="semantic_scholar"、is_hot_paper=true

### Requirement: 终端摘要输出
系统 SHALL 在搜索完成后向 stderr 输出简要的统计摘要。

#### Scenario: 搜索摘要
- **WHEN** 搜索和评分完成后
- **THEN** 系统在 stderr 输出：搜索到的论文总数、去重后数量、top N 论文的标题和评分
