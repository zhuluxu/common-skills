## 1. SKILL.md 重构——整体结构

- [x] 1.1 重写 SKILL.md 的头部元数据（name、description），更新为"论文搜索与阅读"双能力 skill
- [x] 1.2 添加"模式判断"部分：根据用户输入（URL vs 无 URL）自动选择搜索模式或阅读模式

## 2. 搜索模式——工作流描述

- [x] 2.1 添加"步骤1：配置加载"部分——描述如何获取配置文件路径（参数 > 环境变量 > 默认配置），解析 research_interests.yaml
- [x] 2.2 添加"步骤2：论文搜索"部分——描述调用 `scripts/search_arxiv.py` 的完整命令行及参数说明（--config, --output, --max-results, --top-n, --categories, --target-date, --focus, --days, --skip-hot-papers）
- [x] 2.3 添加"步骤3：读取和展示结果"部分——描述如何读取 `arxiv_filtered.json`，向用户展示 top N 论文的标题、评分、匹配领域、arXiv 链接
- [x] 2.4 添加"评分体系说明"部分——文档化四维评分（相关性/新近性/热门度/质量）的计算规则和权重

## 3. 阅读模式——保留原有能力

- [x] 3.1 保留原有的 URL → 下载 → 解压 → 阅读 → 生成报告 工作流，整合到 SKILL.md 的"阅读模式"章节

## 4. 脚本文档化

- [x] 4.1 在 SKILL.md 中添加"脚本说明"部分，文档化 `search_arxiv.py`、`scan_existing_notes.py`、`link_keywords.py`、`common_words.py` 的功能和 CLI 接口
- [x] 4.2 在 SKILL.md 中添加"依赖项"部分，列出 Python 3.x、PyYAML、可选 requests 库及安装命令

## 5. 配置文件模板

- [x] 5.1 在 SKILL.md 中添加 `research_interests.yaml` 配置文件的示例模板，说明各字段含义（research_domains、keywords、arxiv_categories、priority、excluded_keywords、semantic_scholar_api_key）

## 6. 验证

- [x] 6.1 验证 SKILL.md 中所有脚本调用命令在当前目录结构下可正确执行
- [x] 6.2 验证搜索模式和阅读模式的工作流描述完整且无遗漏
