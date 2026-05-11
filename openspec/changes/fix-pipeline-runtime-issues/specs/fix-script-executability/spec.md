## MODIFIED Requirements

### Requirement: 脚本调用方式统一为 python -m

系统 SHALL 将 SKILL.md 中所有脚本调用从 `python scripts/xxx.py` 改为 `python -m scripts.xxx` 方式，确保相对导入的脚本可以正确执行。

#### Scenario: 直接运行脚本失败
- **WHEN** 使用 `python scripts/resolve_paper.py --input "..."` 直接运行
- **THEN** 报错 `ImportError: attempted relative import with no known parent package`

#### Scenario: 模块方式运行成功
- **WHEN** 使用 `cd "$SKILL_DIR" && python -m scripts.resolve_paper --input "..."` 运行
- **THEN** 脚本正确导入 `scripts.common` 并执行成功