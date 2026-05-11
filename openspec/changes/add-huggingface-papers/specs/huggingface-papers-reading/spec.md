## ADDED Requirements

### Requirement: HF markdown 全文获取

系统 SHALL 在阅读模式步骤3中增加 Hugging Face markdown 全文作为论文内容获取途径，优先级在 TeX 源码之后、PDF 之前。

#### Scenario: TeX 不可用，HF markdown 可用
- **WHEN** 论文的 TeX 源码不可用（下载失败或论文无 TeX 源码）
- **THEN** 系统尝试 `curl https://huggingface.co/papers/{arxiv_id}.md` 获取 markdown 全文
- **AND** 使用 HF markdown 作为证据提取的输入

#### Scenario: HF markdown 不可用
- **WHEN** HF markdown 返回 404（论文未在 HF 索引或无 HTML 版本）
- **THEN** 系统 fallback 到 PDF 获取模式

#### Scenario: 内容获取优先级
- **WHEN** 用户进入阅读模式
- **THEN** 系统按以下优先级获取论文内容：TeX 源码 → HF markdown → PDF
- **AND** 在笔记 frontmatter 的 `source_type` 字段标记实际使用的来源（`tex` / `hf_markdown` / `pdf`）

### Requirement: HF 元数据增强

系统 SHALL 在阅读模式步骤2（收集元数据）中调用 HF Papers API 获取关联资源。

#### Scenario: 论文在 HF 上有关联资源
- **WHEN** 论文在 Hugging Face 上有关联的 models/datasets/spaces/GitHub 仓库
- **THEN** 系统调用以下 API 获取关联资源：
  - `GET https://huggingface.co/api/papers/{paper_id}` 获取元数据
  - `GET https://huggingface.co/api/models?filter=arxiv:{paper_id}` 获取关联模型
  - `GET https://huggingface.co/api/datasets?filter=arxiv:{paper_id}` 获取关联数据集
  - `GET https://huggingface.co/api/spaces?filter=arxiv:{paper_id}` 获取关联 Spaces
- **AND** 将关联资源信息合并到元数据中

#### Scenario: 论文不在 HF 索引中
- **WHEN** HF Papers API 返回 404
- **THEN** 系统跳过 HF 元数据，继续使用 arXiv/Semantic Scholar 元数据

### Requirement: 关联资源章节输出

系统 SHALL 在生成的 Obsidian 笔记中新增 `## 关联资源` 章节（如有关联资源）。

#### Scenario: 有关联资源
- **WHEN** HF 元数据包含关联的 models/datasets/spaces/GitHub 仓库
- **THEN** 笔记中新增 `## 关联资源` 章节，按类型列出：
  - **Models**: 关联的 Hugging Face 模型链接
  - **Datasets**: 关联的数据集链接
  - **Spaces**: 关联的在线演示链接
  - **GitHub**: 项目仓库链接
 - **AND** 每个条目包含名称和 URL

#### Scenario: 无关联资源
- **WHEN** 论文在 HF 上无关联资源
- **THEN** 不生成 `## 关联资源` 章节