## ADDED Requirements

### Requirement: 12 步流水线执行
系统 SHALL 按顺序执行 DeepPaperNote 的 12 步流水线，不得跳过必需步骤。

#### Scenario: 正常流水线执行
- **WHEN** 用户提供论文标识（URL、DOI、标题、arXiv ID）
- **THEN** 系统依次执行：resolve paper → collect metadata → fetch PDF → extract evidence → extract PDF assets → plan figures → build synthesis bundle → model planning → model writing → lint → final readability review → write to Obsidian

#### Scenario: 步骤失败处理
- **WHEN** 某个必需步骤失败
- **THEN** 系统仅允许三种操作：(1) 重试该步骤 (2) 进入明确允许的 fallback (3) 停止并报告阻塞的步骤和未完成的下游步骤

### Requirement: PDF 优先策略
系统 SHALL 优先获取 PDF，仅在 PDF 不可用或用户明确要求时使用 TeX 源码。

#### Scenario: PDF 可用
- **WHEN** 论文有可访问的 PDF（本地、Zotero、arXiv、DOI）
- **THEN** 系统使用 PDF 进行证据提取和图片提取

#### Scenario: PDF 不可用，TeX 可用
- **WHEN** PDF 无法获取但 arXiv 提供 TeX 源码
- **THEN** 系统回退到 TeX 源码阅读模式，并明确告知用户使用了 fallback

#### Scenario: 用户明确要求 TeX
- **WHEN** 用户明确说"我要看 LaTeX 源码"或"下载 TeX 文件"
- **THEN** 系统跳过 PDF 获取，直接使用 TeX 源码模式

### Requirement: 调用本地脚本
系统 SHALL 调用 paper-search-reader/scripts/ 目录下的脚本，不依赖外部项目。

#### Scenario: 使用 run_pipeline.py
- **WHEN** 需要执行完整流水线
- **THEN** 系统调用 `scripts/run_pipeline.py` 并传递论文标识

#### Scenario: 脚本路径
- **WHEN** 调用任何脚本
- **THEN** 系统使用相对于 SKILL_DIR 的路径（如 `cd "$SKILL_DIR" && python scripts/run_pipeline.py`）

### Requirement: Python 版本检查
系统 SHALL 在运行 DeepPaperNote 脚本前检查 Python 版本，确保 >=3.10。

#### Scenario: Python 版本兼容
- **WHEN** 默认 `python3` 版本 <3.10
- **THEN** 系统自动查找兼容的解释器（python3.12、python3.11、python3.10、/opt/anaconda3/bin/python3 等）并使用第一个找到的

#### Scenario: 无兼容解释器
- **WHEN** 找不到 Python >=3.10
- **THEN** 系统停止并明确告知用户需要 Python >=3.10

### Requirement: Model-first 原则
系统 SHALL 让 Claude 模型负责理解论文和写作笔记，脚本仅负责数据收集和结构化。

#### Scenario: 读取 synthesis bundle
- **WHEN** `build_synthesis_bundle.py` 完成
- **THEN** Claude 读取 bundle JSON，理解论文内容，创建 note_plan，然后写作笔记

#### Scenario: 不依赖脚本理解
- **WHEN** 生成笔记
- **THEN** Claude 不依赖脚本的摘要或关键词，而是从 bundle 的原始证据中推断
