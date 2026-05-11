## 1. SKILL.md 搜索模式更新

- [x] 1.1 更新模式判断，新增 HF URL 识别（`huggingface.co/papers/`、`hf.co/papers/`、`{ID}.md` 后缀）
- [x] 1.2 在搜索模式步骤中新增 HF Daily Papers 搜索流程（步骤2之后）
- [x] 1.3 在搜索模式评分体系中新增 HF 热门度加分（+0.5）和 HF 关联资源加分（+0.3）
- [x] 1.4 在搜索结果输出中新增 HF 来源标记和关联资源计数
- [x] 1.5 在 Focus 模式中新增 HF Papers 语义搜索（`/api/papers/search?q=`）

## 2. SKILL.md 阅读模式更新

- [x] 2.1 在阅读模式步骤1（解析论文身份）中新增 HF URL 解析逻辑
- [x] 2.2 在阅读模式步骤2（收集元数据）中新增 HF API 元数据增强（关联 models/datasets/spaces/GitHub）
- [x] 2.3 在阅读模式步骤3（获取论文内容）中新增 HF markdown 全文获取，优先级：TeX → HF markdown → PDF
- [x] 2.4 在阅读模式步骤9（模型写作笔记）中新增 `## 关联资源` 章节模板
- [x] 2.5 新增 `source_type: "hf_markdown"` 标记说明

## 3. 脚本更新——search_arxiv.py

- [x] 3.1 新增 HF Daily Papers API 调用函数（`fetch_hf_daily_papers`）
- [x] 3.2 新增 HF Papers Search API 调用函数（`search_hf_papers`）
- [x] 3.3 新增 HF 结果到标准格式的转换函数（`_normalize_hf_paper`）
- [x] 3.4 修改主搜索流程，将 HF 结果合并到结果池并去重
- [x] 3.5 新增 CLI 参数 `--skip-hf-papers`（跳过 HF 搜索）
- [x] 3.6 新增评分加分逻辑（HF 热门 +0.5，HF 关联资源 +0.3）

## 4. 脚本更新——resolve_paper.py

- [x] 4.1 新增 HF URL 解析（从 `huggingface.co/papers/{id}` 或 `hf.co/papers/{id}` 提取 arXiv ID）— 实现在 common.py 的 `parse_hf_paper_id` 和 `infer_source_type`
- [x] 4.2 新增 HF markdown URL 解析（从 `{id}.md` 后缀提取 arXiv ID）— 实现在 `parse_hf_paper_id`

## 5. 脚本更新——collect_metadata.py

- [x] 5.1 新增 HF Papers API 元数据获取函数（`fetch_hf_paper_metadata`）
- [x] 5.2 新增 HF 关联资源获取函数（`fetch_hf_linked_resources`：models/datasets/spaces）
- [x] 5.3 修改元数据合并逻辑，将 HF 数据合并到元数据输出

## 6. 脚本更新——common.py

- [x] 6.1 新增 HF Paper ID 解析工具函数（`parse_hf_paper_id`）
- [x] 6.2 新增 HF API 请求工具函数（`fetch_hf_json`，带错误处理和重试）

## 7. 依赖和配置

- [x] 7.1 更新 SKILL.md 依赖项说明（HF API 无需额外依赖，使用 requests/urllib）
- [x] 7.2 在配置文件中新增 HF 搜索开关（`enable_hf_papers: true`）

## 8. 验证

- [x] 8.1 验证 HF URL 解析正确（`huggingface.co/papers/2602.08025` → `2602.08025`）
- [x] 8.2 验证 HF Daily Papers API 调用正常返回
- [x] 8.3 验证 HF Search API 调用正常返回
- [x] 8.4 验证搜索结果去重合并正确
- [x] 8.5 验证阅读模式 HF markdown 获取和 fallback 逻辑