## ADDED Requirements

### Requirement: 本地库优先搜索
系统 SHALL 在解析论文前检查 Zotero 集成，若可用则优先从本地库搜索。

#### Scenario: Zotero 可用性检查
- **WHEN** 开始解析论文
- **THEN** 系统尝试调用 Zotero MCP 工具（如搜索标题），若成功则标记 Zotero 可用，若失败则记录"Zotero not available"并继续

#### Scenario: 本地库搜索
- **WHEN** Zotero 可用且用户提供标题、DOI 或 arXiv ID
- **THEN** 系统首先在本地 Zotero 库中搜索，若找到则使用该结果作为规范身份

#### Scenario: 获取本地 PDF 附件
- **WHEN** Zotero 找到论文且有附件
- **THEN** 系统使用 `locate_zotero_attachment.py` 定位本地 PDF 路径（在 Zotero storage/ 目录下）

### Requirement: 网络 fallback
系统 SHALL 在本地库未找到论文时回退到网络搜索。

#### Scenario: 本地库无结果
- **WHEN** Zotero 搜索无结果
- **THEN** 系统使用网络 API（arXiv、Semantic Scholar、DOI）搜索论文元数据

#### Scenario: 本地元数据 + 网络 PDF
- **WHEN** Zotero 找到论文但无本地附件
- **THEN** 系统使用 Zotero 的元数据（避免标题歧义），但从网络获取 PDF
