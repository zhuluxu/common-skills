## ADDED Requirements

### Requirement: 生成高质量 Markdown 笔记
系统 SHALL 生成结构化、证据驱动、深度分析的 Obsidian 笔记。

#### Scenario: 笔记结构
- **WHEN** 生成笔记
- **THEN** 笔记包含：frontmatter（title、authors、year、tags）、原文摘要翻译、创新点、一句话总结、研究问题、任务定义、数据/材料、方法、实验结果、深度分析、局限性、为何值得保留

#### Scenario: 使用真实标题层级
- **WHEN** 组织笔记内容
- **THEN** 使用真实的 Markdown 标题层级（`#`、`##`、`###`），不使用加粗文本模拟标题

#### Scenario: 技术细节深度
- **WHEN** 论文包含重要公式、算法、架构
- **THEN** 笔记包含关键公式（使用 `$...$` 或 `$$...$$`）、算法伪代码、架构说明，而非仅高层摘要

### Requirement: 图片嵌入
系统 SHALL 在笔记中嵌入图片，使用 Obsidian wikilink 语法。

#### Scenario: 嵌入真实图片
- **WHEN** 图片已提取并匹配到占位符
- **THEN** 使用 `![[images/fig1.png|600]]` 格式嵌入图片

#### Scenario: 保留占位符
- **WHEN** 图片未提取或匹配失败
- **THEN** 使用文本占位符 `[图 1: caption text]`

### Requirement: 混合语言校验
系统 SHALL 使用 `lint_note.py` 校验笔记，确保通过 style gate（无混合中英文行）。

#### Scenario: Lint 失败修复
- **WHEN** `lint_note.py` 输出 `passes_style_gate: false`
- **THEN** 系统修复报告的问题并重新运行 lint，直到通过

#### Scenario: Final readability review
- **WHEN** lint 通过后
- **THEN** 系统进行最终可读性审查，平滑不自然的中文表达，重写普通英文短语为自然中文，保留稳定的专有名词

### Requirement: 保存到 Obsidian
系统 SHALL 使用 `write_obsidian_note.py` 将笔记保存到 Obsidian vault。

#### Scenario: 选择 domain 文件夹
- **WHEN** 保存笔记前
- **THEN** 系统优先选择已有的 domain 文件夹（如 "大模型"、"多模态"），仅在无合适匹配时创建新 domain

#### Scenario: 创建论文文件夹
- **WHEN** 保存笔记
- **THEN** 系统在 domain 下创建论文同名文件夹，包含笔记 Markdown 和 `images/` 子文件夹

#### Scenario: Vault 不可写
- **WHEN** 配置的 vault 路径不可写
- **THEN** 系统请求用户权限提升，不自动降级到 workspace 输出
