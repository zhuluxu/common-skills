## 1. 修复脚本调用方式

- [x] 1.1 将 SKILL.md 中所有 `cd "$SKILL_DIR" && $PY_EXEC scripts/xxx.py --` 改为 `cd "$SKILL_DIR" && $PY_EXEC -m scripts.xxx --`
- [x] 1.2 将 SKILL.md 中所有 `python scripts/xxx.py` 调用改为 `python -m scripts.xxx`

## 2. 新增 fetch_hf_markdown.py 脚本

- [x] 2.1 创建 `scripts/fetch_hf_markdown.py`，使用 Python urllib 获取 HF markdown 全文
- [x] 2.2 脚本支持 `--arxiv-id` 和 `--output` 参数
- [x] 2.3 脚本处理 404（论文未索引）和网络错误，返回适当的退出码
- [x] 2.4 更新 SKILL.md 步骤3 中 HF markdown 获取命令，从 curl 改为 Python 脚本

## 3. 修复 arXiv URL 解析 fallback

- [x] 3.1 在 `common.py` 的 `resolve_reference` 中，`arxiv_url` 分支 arXiv API 失败时增加 HF API fallback
- [x] 3.2 HF fallback 使用已有的 `fetch_hf_json` 函数获取元数据
- [x] 3.3 HF fallback 成功时设置 `source_type: "hf_paper_url"`

## 4. 验证

- [x] 4.1 验证 `python -m scripts.resolve_paper --input "https://arxiv.org/abs/2501.04961"` 正确解析（返回 title + arxiv_id）
- [x] 4.2 验证 `python -m scripts.fetch_hf_markdown --arxiv-id 2501.04961 --save-dir /tmp/paper_md` 正确获取 markdown（110491 chars）
- [x] 4.3 验证 arXiv API 限流时 HF fallback 正常工作（`_try_hf_fallback` 返回正确元数据）