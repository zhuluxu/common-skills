## ADDED Requirements

### Requirement: Placeholder-first 策略
系统 SHALL 为所有重要图表创建占位符，仅在高置信度匹配时替换为真实图片。

#### Scenario: 创建图表占位符
- **WHEN** 从 evidence 中识别出重要图表（Fig. 1、Table 2 等）
- **THEN** 系统在 figure_plan.json 中为每个图表创建占位符条目，包含 id、caption、kind、section、priority

#### Scenario: 高置信度图片替换
- **WHEN** 提取的 PDF 图片与占位符明确匹配（通过 caption 文本、页码、位置）
- **THEN** 系统将占位符的 `insert_mode` 设为 "replace"，并记录图片路径

#### Scenario: 低置信度保留占位符
- **WHEN** 图片匹配不确定或提取失败
- **THEN** 系统保留占位符，`insert_mode` 为 "placeholder"，在笔记中显示为 `[图 1: caption text]`

### Requirement: 从 PDF 提取图片
系统 SHALL 使用 `extract_pdf_assets.py` 从 PDF 提取页面级图片资源。

#### Scenario: 对象级图片提取
- **WHEN** PDF 包含嵌入的图片对象
- **THEN** 系统提取每个图片对象，记录页码、图片索引、尺寸、提取方法

#### Scenario: 图片元数据记录
- **WHEN** 图片提取完成
- **THEN** 系统在 pdf_assets.json 中记录每个图片的元数据（page_number、image_index、width、height、extraction_method）

### Requirement: 保留原始编号
系统 SHALL 在笔记中保留论文的原始图表编号（如 Fig. 1、Table 2），不重新编号。

#### Scenario: 图表引用
- **WHEN** 在笔记中引用图表
- **THEN** 使用原始编号，如 "如 Fig. 1 所示" 或 "Table 2 展示了..."
