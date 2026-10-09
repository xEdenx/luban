# ADR-0006：以原生追加模板准备最小团队 Preset

日期：2026-10-10。状态：实验候选；用户同意先核验最小 Preset，正式团队接入待 playbook 与真实客户端验证。

## 背景

共享入口已要求记录风险、约束版本与确认依据，但原生 Spec/Plan 模板未显式承载这些团队字段。用户另有 spec coding playbook，包含团队习惯与实现方式，位于工作电脑，当前无法读取。

## 决策

使用 Spec Kit 1.1.2 原生 Preset 的 `append` 策略，为 Spec/Plan 各追加一个小节。只声明两个模板贡献，保留原生底层模板；规则与角色从业务工程权威来源引用，不复制原生开发流程，不增加命令覆盖、规则引擎或审批服务。

现有 playbook 在工作电脑按条款核对：长期约束保留权威位置，操作可由 Skill 引用，重复输出格式按需进入内部 Preset；实现建议与强制规则区分，冲突先裁决。公共候选仅包含已确认的通用字段，未导入或推测 playbook 内容。

## 证据与边界

个人电脑两项生命周期测试通过，覆盖 generic Skills/命令文件两种布局、安装与原生 Python 脚本生成、项目文件保护及移除；项目完整覆盖模板优先，无效策略生成失败。详见[核验记录](../research/native-capability-audit.md)。

`preset resolve` 只显示最高层路径与组合链，不输出可直接复制的完整组合模板；使用原生组合解析或生成脚本。generic 不注册 Preset 命令覆盖，Lean 自包含命令也可能绕过模板，不能把本地生成测试当作实际 Agent 行为验证。

现有 Extension 与五个薄入口的注册、版本和 L0–L3/MR 路径保持不变。CLI Workflow 等实际派发能力确认，Bundle 等组件与客户端稳定验证后再正式组合。主设计见[技术设计](../technical-design.md)，操作见[Preset 说明](../../presets/team-baseline/README.md)。
