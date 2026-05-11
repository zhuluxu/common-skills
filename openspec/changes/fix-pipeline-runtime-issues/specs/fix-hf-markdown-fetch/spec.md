## ADDED Requirements

### Requirement: HF markdown 全文获取使用 Python urllib

系统 SHALL 将 HF markdown 全文获取从 shell curl 改为 Python urllib 脚本调用，确保网络兼容性。

#### Scenario: curl 因 TLS 问题失败
- **WHEN** shell 命令 `curl -sL "https://huggingface.co/papers/{ID}.md"` 因 TLS 连接重置失败
- **THEN** Python urllib 同一请求成功返回 markdown 内容

#### Scenario: 通过脚本获取 HF markdown
- **WHEN** 执行 `cd "$SKILL_DIR" && python -m scripts.fetch_hf_markdown --arxiv-id 2501.04961 --output /tmp/paper_md/2501.04961.md`
- **THEN** 脚本使用 urllib 请求 `https://huggingface.co/papers/{ID}.md`
- **AND** 成功时将 markdown 内容写入输出文件
- **AND** 失败时（404 或网络错误）返回非零退出码和错误信息

#### Scenario: 论文未在 HF 索引
- **WHEN** HF 返回 404
- **THEN** 脚本输出错误信息并返回退出码，流水线 fallback 到 PDF