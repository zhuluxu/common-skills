## Context

阅读模式流水线在首次端到端执行中暴露三类问题：

1. **脚本导入问题**：所有 DeepPaperNote 脚本使用相对导入（`from .common import`），当直接运行 `python scripts/resolve_paper.py --input ...` 时报 `ImportError: attempted relative import with no known parent package`。解决方式有二：(a) 用 `python -m scripts.resolve_paper` 方式运行；(b) 添加 `__main__.py` 入口。方案 (a) 更简洁，但要求 SKILL.md 中所有脚本调用都改为 `-m` 方式。

2. **HF markdown 获取问题**：SKILL.md 步骤3 使用 `curl -sL "https://huggingface.co/papers/{ID}.md"` 获取 markdown，但实际执行时 curl 因 TLS 连接重置失败（exit code 35），而 Python urllib 同一 URL 可以成功。原因是 curl 和 urllib 的 TLS 行为不同（可能是 IPv6/IPv4 选择或 SNI 问题）。

3. **arXiv API 限流**：`resolve_paper.py` 调用 arXiv API 时被限流（"Rate exceeded"），导致 arXiv URL 解析回退到 title_query，最终输出原始 URL 作为标题而非论文元数据。

## Goals / Non-Goals

**Goals:**
- 修复所有 DeepPaperNote 脚本的可执行性，使 12 步流水线可以端到端自动运行
- 将 HF markdown 获取从 shell curl 改为 Python urllib，确保网络兼容性
- 修复 arXiv API 限流时的 fallback 行为，确保 URL 输入总能得到有效的论文身份
- 统一 SKILL.md 中所有脚本调用方式为一贯的 `cd "$SKILL_DIR" && python -m scripts.xxx`

**Non-Goals:**
- 不重构脚本目录结构（保持 scripts/ 下平铺）
- 不改变文件输出格式或路径约定
- 不新增功能（仅修复已有的）

## Decisions

### Decision 1: 统一使用 `python -m` 方式调用脚本

**选择**：将 SKILL.md 中所有 `python scripts/xxx.py` 调用改为 `python -m scripts.xxx` 方式。

**理由**：
- 相对导入的脚本必须以模块方式运行
- `python -m scripts.xxx` 是 Python 标准做法
- 避免为每个脚本添加 `__main__.py` 或修改导入方式

**替代方案**：
- 添加 `__main__.py` 入口（被拒：需要修改每个脚本文件）
- 修改相对导入为绝对导入（被拒：脚本间有正确的相对依赖关系，不应破坏）

### Decision 2: 新增 `fetch_hf_markdown.py` 脚本获取 HF markdown

**选择**：新增 `scripts/fetch_hf_markdown.py`，使用 Python urllib 获取 HF markdown 全文。

**理由**：
- Python urllib 的 TLS/IP 连接策略比 curl 更健壮（实际测试已证明）
- 脚本可以作为流水线步骤被 `python -m` 调用
- 与已有脚本（fetch_pdf.py）风格一致

**替代方案**：
- 在 shell 中调用 Python 一行命令（被拒：不利于错误处理和输出格式化）
- 在 SKILL.md 中使用 `python -c`（被拒：长命令不利于维护）

### Decision 3: arXiv URL 解析增加重试和 HF fallback

**选择**：在 `resolve_reference` 的 `arxiv_url` 分支中，arXiv API 失败时增加 HF API fallback——用 HF Papers API 获取元数据。

**理由**：
- arXiv 限流是常见问题，HF API 是独立的数据源
- HF API 已经在 `collect_metadata.py` 中使用，有现成的请求逻辑
- 用户提供的 arXiv URL 应该总能被解析，不应因临时限流而回退到 title_query

## Risks / Trade-offs

- **`python -m` 调用方式** → 需要更新 SKILL.md 中所有脚本调用。风险低但修改范围大
- **HF API fallback** → HF 可能也不返回数据（论文未索引），此时确实需要回退到 title_query。这是可接受的
- **新增脚本** → 增加 `fetch_hf_markdown.py` 一个文件，维护成本很低