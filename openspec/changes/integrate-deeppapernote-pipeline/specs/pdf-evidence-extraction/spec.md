## ADDED Requirements

### Requirement: 从 PDF 提取结构化证据
系统 SHALL 使用 `extract_evidence.py` 从 PDF 提取结构化证据包，包含 sections、candidate chunks、captions、metrics。

#### Scenario: 提取 section 文本
- **WHEN** PDF 可读
- **THEN** 系统提取 abstract、introduction、method、experiment、conclusion、data 等 section 的文本

#### Scenario: 提取 candidate chunks
- **WHEN** 提取 section 文本后
- **THEN** 系统为每个 section 生成最多 12 个候选 chunks（每个 chunk 2 句话，最多 520 字符）

#### Scenario: 提取 figure 和 table captions
- **WHEN** PDF 包含图表
- **THEN** 系统提取所有 figure 和 table 的 caption 文本，保留原始编号（如 Fig. 1、Table 2）

#### Scenario: 提取 metrics 和数值声明
- **WHEN** PDF 包含实验结果
- **THEN** 系统提取包含数值、百分比、对比的句子（如 "achieves 95% accuracy"、"outperforms baseline by 10%"）

### Requirement: 证据质量标记
系统 SHALL 在 evidence_pack.json 中标记证据质量和提取失败信息。

#### Scenario: 证据质量评估
- **WHEN** 证据提取完成
- **THEN** 系统在 evidence_pack.json 中包含 `evidence_quality` 字段（如 "high"、"medium"、"degraded"）

#### Scenario: 提取失败记录
- **WHEN** 某些 section 或 caption 提取失败
- **THEN** 系统在 `extraction_failures` 字段中记录失败的部分和原因
