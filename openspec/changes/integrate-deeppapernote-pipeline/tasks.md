## 1. 复制 DeepPaperNote 脚本

- [x] 1.1 复制所有 DeepPaperNote 脚本到 paper-search-reader/scripts/ 目录（16 个脚本文件）
- [x] 1.2 验证复制后的脚本可以独立运行（测试 common.py 导入）
- [x] 1.3 检查是否需要调整脚本中的路径引用（如 references/ 目录）

## 2. SKILL.md 阅读模式重构——整体结构

- [ ] 2.1 重写阅读模式的开头说明，明确 PDF 优先策略和 TeX fallback
- [ ] 2.2 移除 DeepPaperNote 外部引用说明（因为已复制到本地）
- [ ] 2.3 添加环境变量配置说明（OBSIDIAN_VAULT_PATH）

## 3. 阅读模式——完整流水线描述

- [ ] 3.1 添加"步骤0：环境检查"——检查 Python 版本（>=3.10）、Zotero 可用性
- [ ] 3.2 添加"步骤1：解析论文身份"——调用 scripts/resolve_paper.py 或 Zotero 搜索
- [ ] 3.3 添加"步骤2：收集元数据"——调用 scripts/collect_metadata.py
- [ ] 3.4 添加"步骤3：获取 PDF"——调用 scripts/fetch_pdf.py，说明 PDF 优先策略和 TeX fallback
- [ ] 3.5 添加"步骤4：提取证据"——调用 scripts/extract_evidence.py，说明证据包结构
- [ ] 3.6 添加"步骤5：提取 PDF 图片"——调用 scripts/extract_pdf_assets.py
- [ ] 3.7 添加"步骤6：规划图表"——调用 scripts/plan_figures.py，说明 placeholder-first 策略
- [ ] 3.8 添加"步骤7：构建 synthesis bundle"——调用 scripts/build_synthesis_bundle.py
- [ ] 3.9 添加"步骤8：模型规划笔记"——Claude 读取 bundle 并创建 note_plan
- [ ] 3.10 添加"步骤9：模型写作笔记"——Claude 根据 bundle 和 plan 写作完整笔记
- [ ] 3.11 添加"步骤10：Lint 校验"——调用 scripts/lint_note.py，说明 style gate 和修复循环
- [ ] 3.12 添加"步骤11：最终可读性审查"——Claude 进行语言润色
- [ ] 3.13 添加"步骤12：保存到 Obsidian"——调用 scripts/write_obsidian_note.py

## 4. TeX Fallback 模式

- [ ] 4.1 保留原有的 TeX 源码阅读流程，作为独立的 fallback 章节
- [ ] 4.2 添加触发条件说明（PDF 不可用或用户明确要求）

## 5. 脚本文档化

- [ ] 5.1 添加"脚本说明"部分，列出所有复制的脚本及其功能
- [ ] 5.2 添加脚本调用示例（使用本地 scripts/ 路径和参数）
- [ ] 5.3 添加 Python 版本检查逻辑的示例代码

## 6. 依赖项更新

- [ ] 6.1 更新依赖项列表，添加 PyMuPDF (fitz)、pypdf、pdfplumber
- [ ] 6.2 添加 Zotero MCP 工具的可选依赖说明
- [ ] 6.3 移除 DeepPaperNote 项目依赖说明（已复制到本地）

## 7. 配置文件和环境变量

- [ ] 7.1 移除 DEEPPAPERNOTE_DIR 环境变量说明（不再需要）
- [ ] 7.2 说明 OBSIDIAN_VAULT_PATH 在搜索和阅读模式中的共享使用
- [ ] 7.3 添加 Zotero 配置检查的说明

## 8. 验证

- [ ] 8.1 验证所有复制的脚本在 paper-search-reader/scripts/ 下可正常运行
- [ ] 8.2 验证 Python 版本检查逻辑正确
- [ ] 8.3 验证完整流水线描述无遗漏（12 步全覆盖）
- [ ] 8.4 验证 TeX fallback 逻辑清晰且可触发
