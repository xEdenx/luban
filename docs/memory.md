# 项目记忆与当前进度

更新：2026-10-10。此文件是项目内交接记录，不是全局记忆。设计权威在 technical-design.md，日常规则在 team-operating-profile.md。

## 已确认事实

- 用户要求在 coding 目录创建独立文件夹并 git init；本地项目目录已改为 luban，分支 main；已按用户授权创建并推送到 GitHub public repo [xEdenx/luban](https://github.com/xEdenx/luban)。
- 用户要求先提交当前基线，再补开发同学能直接使用的 L0～L3 操作说明。基线已提交为 e67905e，指南及入口同步单独提交；已按用户后续授权完成首次公开发布。
- 当前在个人电脑讨论、准备材料；未来 GitHub public repo 分发，受 MDM 管控的工作 MacBook 验证。
- 团队使用自部署 GitLab，无法自动触发 CI；手动 Pipeline、Runner、版本/许可和审批权限未知。
- 客户端为 Continue 自研 VS Code 插件与 Qoder 独立 Coding Agent App；实际版本和加载能力未知。
- 技术路线已明确：Spec Kit 1.x 原生优先、Flow-forward、L0–L3、AC-to-Test、AGENTS.md + Skills + CI、未来 Bundle。
- 用户确认明确混合生命周期：业务变更沿用 Flow-forward；全局约束与长期设计按 Living Spec 思路持续维护，每类规则有唯一权威来源。修改全局约束先确认，冲突暂停相关实施并裁决，确认与验收关联适用的约束版本；ADR 保留历史，以新记录补充或取代。
- 用户进一步确认 L1 单 MR 分阶段，先确认具体 Spec/AC 版本，再实现，最后审核；最终交付通常由另一位开发者审核，例外明确记录。
- 用户确认 L2 单 MR 分阶段并确认技术方案；L3 Spec MR + 实现 MR。
- 用户确认 L0/L1 模块负责人、L2/L3 技术负责人确认等级；降级需相应负责人留痕。Agent 推荐等级，发现新风险先停止相关实施。
- 用户确认第一版面向 Java 后端、Maven、Spring Boot；精确版本、测试框架、profile 和报告配置未提供。
- 用户同意先核验最小团队 Preset，并说明已有 spec coding playbook 在工作电脑，包含团队习惯与实现方式；当前未读取其内容。接入时核对版本、维护人、适用范围及强制/建议/历史描述，复用原权威位置，内部资料不回传公开仓库。
- 用户澄清：开发者提供需求文档或功能变化描述，调用 Skill/入口后，由 Agent 自动生成规范 Spec，关键内容人工确认后继续规划、编码、验证和交付；不是要求开发者逐条运行原生命令。

- 用户进一步明确不能完全依靠开发者自行评级；默认统一 start 入口，由 Agent 按工程证据与规则下限评估、负责人确认、实施复评和最终 Review 复核，四级入口不得绕过。

## 本轮已完成

- 导入并维护单一主设计与实施接力，添加 Agent 指南、ADR 和项目状态。
- 补充操作基线提案、GitLab 手动验收路径、工作电脑验证手册、正负验证案例、公开迁移说明、MR 与验收模板。
- 核验 Spec Kit v1.1.2 / commit 959e866caa3618bf3dc290d5dca33394365af9c6，记录精确来源与本地包版本。
- 在个人电脑隔离环境安装并运行 CLI，生成 generic Skills，安装 Bug 与 Lean，校验官方 bugfix Bundle 清单。
- 虚构 Workflow gate 验证：无 verdict 暂停，提供 approve 恢复完成，reject 终止；这不代表可信人工批准。
- 发现 CLI 1.1.2 无 workflow validate 命令；默认 speckit Workflow 未包含 Converge 和真实测试，应显式执行或后续原生组合。
- 补充 AC-to-Test JSON 0.1、虚构 Spec/映射/XML、Python 标准库检查器与操作说明；不接管原生开发流程。
- 检查器 24 个自检在个人电脑 Python 3.14.8 与 Apple Python 3.9.6 均通过，覆盖正例、缺映射、跳过/失败、缺报告、旧报告、执行非零和被测版本变化等。全部使用虚构报告、模拟命令与临时 Git 仓库，未运行真实 Maven/Spring Boot 工程。
- 上一轮补 developer-guide.md 人工操作手册并提交 d7a181f；本轮按用户澄清改成调用/输入/确认/核对交付的指南，维护者安装与调试另见 skill-integration.md。
- 实现 team-sdlc Extension 0.1.0，注册 L0～L3 四命令，通过原生 generic 生成四 Skill 或命令文件；共享会话执行约定，复用原生核心能力，见 ADR-0004。
- 检查器唯一实现移入 Extension，旧 scripts 路径保留兼容启动器；原生安装同时携带共享规则和脚本，避免个人绝对路径依赖。
- 26 个自检在本机 Python 3.14.8 通过：原有 24 个检查器测试 + 2 个原生安装/移除、文件保护和随包脚本测试。不是模型行为验证，没有在两个客户端或真实 Maven 工程执行。
- 实测官方 speckit CLI Workflow + generic 在 specify 步骤无法派发，因此采用会话内 Skill 衔接；原生生成的 compatibility 字段不被 skill-creator 严格校验器接受，最小校验副本通过，未改受管文件、未宣称客户端兼容。

- 0.1.1 增加默认 start 统一入口和任何入口必经的风险评估规则，复用现有 Spec/Mini-Spec 记录，不增加评级服务。本轮重跑 2 个安装生命周期测试通过，覆盖五入口；检查器实现未改，不重复此前 24 个自检。真实模型评级准确性、暂停和复评仍待验证。

- README 已补七阶段任务流程、封装后四步概览、原生逐步调用与统一入口的 Mermaid 对比图和职责对照；明确原生已有组合能力、保留人工确认及客户端未验证边界。本次仅文档呈现，无架构/执行规则变化，沿用 ADR-0004。

- 按用户最新约束，只增加 skills/ 下 eden-team-speckit-start / l0～l3 五个对外薄入口并同步必要的使用说明；薄入口引用安装内原命令，Spec Kit 原生注册、Extension 清单/版本、内部名称及执行规则均保持不变。此前试加的命令别名和版本调整已撤回。五个薄 Skill 源文件格式检查通过；客户端行为仍未验证。

- 项目品牌确定为鲁班 · Luban，本地目录已改名 luban，README 补充项目定位与获取方式，接入示例路径同步。现有 eden-team-speckit-* Skill、Extension、Spec Kit 原生内容与执行规则不变；本次是命名与公开分发变更，无新架构决策。

- GitHub public repo xEdenx/luban 已创建，首次推送完成；SSH 连接超时后仅将本仓库 origin 改为 HTTPS，使用已登录 gh 的凭证推送。已检查公开文件与既有 Git 历史，未发布 work/、.venv/ 或内部材料；LICENSE 仍待用户选择。

- 主设计 0.6 第 4 节明确混合生命周期、权威来源、冲突处理及约束基线；新增 ADR-0005，保留 ADR-0001 历史正文，并同步 AGENTS.md、README、实施接力、操作基线、共享入口参考及验收模板。未改变原生注册、L0–L3/MR 路径、Extension 版本或检查器/schema。本轮 9 份 Markdown 的 62 个本地文件/标题链接及代码围栏检查通过，git diff --check 通过；客户端遵循、约束变更确认与团队执行仍未验证。

- 新增 team-baseline Preset 0.1.0 实验候选，锁定 Spec Kit 1.1.2，原生 append 为 Spec/Plan 各追加一个通用接力小节；不覆盖命令、Constitution 或具体团队实现方式。新增 ADR-0006、Preset 说明与两个生命周期测试，同步主设计 0.7、接入/工作电脑手册、验证案例、共享参考及版本/核验记录。四项原生生命周期测试通过（两项既有 Extension + 两项新增 Preset）；14 份 Markdown 的 95 个本地文件/标题链接与代码围栏检查、JSON 解析及 git diff --check 通过。检查器实现未改，不重复其既有 24 项自检；内部 playbook、两客户端与实际业务仍未验证，CLI Workflow/Bundle 未实施。

## 阶段状态

| 阶段 | 状态 | 剩余内容 |
|---|---|---|
| T0 环境与原生能力 | 部分完成 | 原生个人电脑核验完成；真实客户端、内部 GitLab 与工作电脑事实待验证 |
| T1 真实最小闭环 | 统一入口与四级路径已实现 | 原生注册安装已验证；尚无实际 Agent 端到端行为与批准的业务试点 |
| T2 AC-to-Test | 实验原型完成 | JSON 0.1/默认 Maven XML 检查器与虚构自检通过；真实工程适配及受管环境待验证 |
| T3 交付约束 | 操作设计已补充 | GitLab MR 模板已有；内部权限、人工执行与合并核验未运行 |
| T4 两客户端 | 安装产物已准备 | 统一入口、四兼容入口和共享依赖已有；插件基线、App 发现/执行/接力仍未验证 |
| T5 复杂任务与新工程 | 未验证 | 实际业务试点与样本指标 |
| T6 官方 Bundle | 未实施 | 最小 Preset 机制候选已本地验证；正式 Bundle 仍待闭环、组件来源与客户端验证 |

## 仍需讨论/收敛

尚待负责人确认的细则：紧急例外的具体审批人/补全期限、试点规模和实际业务 AC。已确认的 MR 路径、分级权限与独立 Review 原则不再重复讨论；具体人员与平台约束能力在工作电脑验证。未回应不等于已批准。

## 下一步

1. 维护可调用入口与开发者指南，真实客户端按“输入 → 起草 → 修订/确认 → 自动实施 → 功能核对”验证；不再把开发者逐条操作清单当成最终产品。
2. 工作电脑先自检检查器，再核验真实 POM/JUnit/报告布局、两个客户端、GitLab 记录/权限和真实业务 AC；必要时最小调整原型，不另建测试平台。
3. 继续维护公开内容边界与版本记录；仓库账号/名称已确定并公开，LICENSE 尚待选择，内部业务验证结果不回传公开仓库。
4. 工作电脑按 work-mac-validation.md 收集事实并逐项验证，内部结果不回传公开仓库。
5. 在工作电脑读取已有 playbook，明确条款的权威来源，按需调整内部 Preset/Skill；验证 team-baseline 组合模板在真实客户端下被正确读取与填写，项目 override/Lean 等组合分别核验。

## 验证材料

具体运行结果与固定上游来源见 [原生能力核验](research/native-capability-audit.md) 和 [版本快照](research/version-baseline.json)。本地完整日志及探针在忽略的 work/；不能将其存在视为工作环境通过。
