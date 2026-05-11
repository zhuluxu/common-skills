## Why

阅读模式流水线在实际执行中暴露了三个代码缺陷：(1) `resolve_paper.py` 因相对导入问题无法直接运行，导致 arXiv URL 无法被解析为论文身份（回退到 title_query 且结果为原始 URL）；(2) HF markdown 全文获取在 shell `curl` 中因网络问题失败（exit code 28/35），但 Python urllib 可以成功——脚本需要使用 Python 方式获取 markdown 而非依赖 shell curl；(3) 这些问题导致整个 12 步流水线无法端到端自动执行，需要人工介入。

## What Changes

- **修复 `resolve_paper.py` 等脚本的可执行性**：添加 `__main__.py` 入口或修改相对导入为可同时支持直接运行和模块运行
- **SKILL.md 步骤3 中 HF markdown 获取从 shell curl 改为 Python 脚本调用**：新增 `scripts/fetch_hf_markdown.py` 脚本，使用 urllib 获取 markdown
- **修复 `resolve_paper.py` 的 arXiv URL 解析**：确保 `infer_source_type` 正确识别后 resolve_reference 能正确走到 `arxiv_url` 分支

## Capabilities

### New Capabilities
- `fetch-hf-markdown`: HF markdown 全文获取脚本，使用 Python urllib（不依赖 shell curl）

### Modified Capabilities
- `resolve-paper`: 修复脚本可执行性和 URL 解析问题
- `deep-reading-pipeline`: 步骤3 的 HF markdown 获取方式从 shell curl 改为 Python 脚本调用

## Impact

- `scripts/resolve_paper.py`：修复导入和 arXiv URL 解析
- `scripts/fetch_hf_markdown.py`：新增脚本
- `SKILL.md`：更新步骤3的 HF markdown 获取命令
- 其他 DeepPaperNote 脚本的 `__main__.py` 入口（如有同样问题一并修复）