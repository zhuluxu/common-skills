## ADDED Requirements

### Requirement: arXiv API 分类搜索
系统 SHALL 通过 `scripts/search_arxiv.py` 调用 arXiv API，按用户配置的分类（如 cs.AI, cs.LG, cs.CL）搜索指定时间窗口内的论文。

#### Scenario: 搜索最近 30 天的论文
- **WHEN** 用户触发搜索且未指定 focus 关键词
- **THEN** 系统使用 arXiv API 搜索最近 30 天内指定分类的论文，返回最多 200 篇结果

#### Scenario: 搜索指定日期范围的论文
- **WHEN** 用户通过 `--target-date` 指定基准日期
- **THEN** 系统以该日期为基准计算时间窗口（最近 N 天 + 过去一年）

### Requirement: arXiv 关键词搜索（Focus 模式）
系统 SHALL 支持用户指定 focus 关键词，在 arXiv 的标题和摘要中进行精确搜索。

#### Scenario: Focus 关键词搜索
- **WHEN** 用户提供 focus 关键词（如 "retrieval augmented generation"）
- **THEN** 系统在 arXiv 标题和摘要中搜索这些关键词，按相关性排序返回结果

#### Scenario: Focus 模式下的评分调整
- **WHEN** 搜索使用 focus 关键词
- **THEN** 相关性评分中 focus 关键词匹配权重为主导（标题匹配 +2.0，摘要匹配 +1.0），原有兴趣域匹配作为 0.3 权重的辅助加分

### Requirement: Semantic Scholar 热门论文检索
系统 SHALL 通过 Semantic Scholar API 搜索过去一年内的高影响力论文，按 influentialCitationCount 排序。

#### Scenario: 搜索热门论文
- **WHEN** 用户触发搜索且未禁用热门论文检索（`--skip-hot-papers`）
- **THEN** 系统使用 Semantic Scholar API 搜索过去一年的高影响力论文，每个查询返回 top 20

#### Scenario: Semantic Scholar API 不可用
- **WHEN** Semantic Scholar API 请求失败或超时
- **THEN** 系统记录警告日志，继续使用 arXiv 搜索结果，不中断整个工作流

### Requirement: 多维评分体系
系统 SHALL 对每篇论文计算四维评分并合成综合推荐分。

#### Scenario: 普通论文评分
- **WHEN** 论文来自 arXiv API 搜索
- **THEN** 系统按以下权重计算综合推荐评分：相关性 40%、新近性 20%、热门度 30%、质量 10%

#### Scenario: 高影响力论文评分
- **WHEN** 论文来自 Semantic Scholar（标记为 is_hot_paper）
- **THEN** 系统使用调整后的权重：相关性 35%、新近性 10%、热门度 45%、质量 10%

#### Scenario: 排除关键词过滤
- **WHEN** 论文标题或摘要包含配置中的排除关键词
- **THEN** 该论文相关性评分为 0，被排除出结果

### Requirement: 研究兴趣配置驱动
系统 SHALL 从 YAML 配置文件读取研究领域定义，包括关键词、arXiv 分类、优先级和排除关键词。

#### Scenario: 加载配置文件
- **WHEN** 用户提供配置文件路径（通过 `--config` 参数或 `OBSIDIAN_VAULT_PATH` 环境变量）
- **THEN** 系统解析 YAML 配置，提取 research_domains 和 excluded_keywords

#### Scenario: 配置文件不存在
- **WHEN** 配置文件路径无效或文件不存在
- **THEN** 系统使用内置默认配置（通用 AI/ML 领域）并记录错误日志

### Requirement: 结果去重
系统 SHALL 对来自 arXiv 和 Semantic Scholar 的论文进行去重。

#### Scenario: 基于 arXiv ID 去重
- **WHEN** 两篇论文具有相同的 arXiv ID
- **THEN** 系统保留评分更高的一篇

#### Scenario: 基于标题去重
- **WHEN** 论文没有 arXiv ID 但标题归一化后（小写+去标点）相同
- **THEN** 系统保留评分更高的一篇
