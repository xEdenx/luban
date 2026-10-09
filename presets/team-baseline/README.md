# team-baseline：最小团队模板 Preset

版本：0.1.0。状态：个人电脑实验候选，锁定 Spec Kit 1.1.2；团队 playbook、实际客户端与业务工程尚未验证。

通过原生 `append` 策略为 `spec-template`、`plan-template` 各追加一个小节，保留底层模板。只提供工程依据、风险、适用约束版本、确认引用和方案符合性字段；原生 AC 场景加 ID 的要求写在提示中，不维护第二份 AC 清单。

规则来源仍是业务工程的权威文档；本 Preset 不定义具体 Java 实现习惯，不提供命令、脚本、Constitution 或 CLI Workflow。五个团队入口和 team-sdlc Extension 保持现有注册与版本。

## 隔离安装与移除

先按[接入说明](../../docs/skill-integration.md)初始化一次性样例，以下命令在该样例根目录运行；不要直接套用到既有业务工程：

```sh
specify preset add --dev /path/to/luban/presets/team-baseline
specify preset info team-baseline --json
specify preset resolve spec-template
specify preset resolve plan-template
```

`preset resolve` 显示优先层与组合链，是诊断信息；输出中的最高层路径可能只是追加片段，不可直接复制为完整 Spec。使用原生模板组合解析或生成脚本取得完整内容。个人电脑实际验证的 Python 生成路径为：

```sh
# 仅在空白样例中创建虚构变更；不用于覆盖已有活跃 Spec。
python .specify/scripts/python/create_new_feature.py --json --number 1 --short-name fixture "Fictional feature"
python .specify/scripts/python/setup_plan.py --json
```

使用具备 PyYAML 的已批准工具解释器（如 Spec Kit 隔离环境的 Python）；脚本另用解释器时，按上游机制配置 `SPECKIT_PYTHON_EXECUTABLE`。这与仅用标准库的 AC 检查器要求不同。

样例中检查新 Spec 同时包含原生场景和“工作说明”，Plan 同时包含 Constitution Check 和“团队约束符合性与接力”。移除后只影响之后的模板解析，已生成的 Spec/Plan 保留：

```sh
specify preset remove team-baseline
```

## 已验证边界与关键限制

- 两种 generic 布局（Skills/命令文件）下，本地安装、原生 Python 脚本组合生成及移除通过。
- 核心模板、核心入口、Constitution、虚构 playbook 与历史 Spec 的内容保持不变；移除不改写已生成 Spec/Plan。
- 项目 `.specify/templates/overrides/` 优先于 Preset：存在完整覆盖模板时，追加字段不会自动出现。由维护者审查合并或由现有团队入口补齐工作说明，不覆盖项目文件。
- 无效模板策略使原生生成失败；安装成功不代表生成、模型填充或客户端行为成功。
- generic 不注册 Preset 命令/Skill 覆盖。本候选只提供模板；本地脚本验证不代表 Agent 已正确消费模板。Lean 的自包含命令也可能不读取这些模板，实际有效组合须另验。

可复现测试：在有 Spec Kit 1.1.2 的环境运行 `python -m unittest discover -s tests -p test_team_preset.py -v`（从标准仓库根目录）。CLI 不在 PATH 时设置 `TEAM_SDLC_SPECIFY` 为实际可执行入口。详见[原生核验](../../docs/research/native-capability-audit.md)。

## 工作电脑上的 playbook 接入

用户已有 spec coding playbook，包含团队习惯和实现方式，但内容只在工作电脑。当前没有读取其内容，不据此推定任何具体规则，也不将内部内容写入公开 Preset。

工作电脑先按[验证手册](../../docs/work-mac-validation.md#31-现有-playbook-与权威来源)核对路径、版本、维护人、适用范围及强制/建议/历史描述。长期约束保留在原权威位置，操作步骤按需由 Skill 引用，可重复的输出格式才考虑进入内部 Preset。与鲁班路线冲突的条款先列差异请负责人裁决；通用候选不自动覆盖内部规范。现有项目文件先比较并在隔离分支验证。
