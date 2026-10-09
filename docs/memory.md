# 项目记忆与当前进度

更新：2026-10-10。此文件是项目内交接记录，不是全局记忆。设计权威在 technical-design.md，日常规则在 team-operating-profile.md。

## 已确认事实

- 用户要求在 coding 目录创建独立文件夹并 git init；本仓库已初始化为 main，尚无远程仓库。
- 当前在个人电脑讨论、准备材料；未来 GitHub public repo 分发，受 MDM 管控的工作 MacBook 验证。
- 团队使用自部署 GitLab，无法自动触发 CI；手动 Pipeline、Runner、版本/许可和审批权限未知。
- 客户端为 Continue 自研 VS Code 插件与 Qoder 独立 Coding Agent App；实际版本和加载能力未知。
- 技术路线已明确：Spec Kit 1.x 原生优先、Flow-forward、L0–L3、AC-to-Test、AGENTS.md + Skills + CI、未来 Bundle。
- 用户进一步确认 L1 单 MR 分阶段，先确认具体 Spec/AC 版本，再实现，最后审核；最终交付通常由另一位开发者审核，例外明确记录。
- 用户确认 L2 单 MR 分阶段并确认技术方案；L3 Spec MR + 实现 MR。
- 用户确认 L0/L1 模块负责人、L2/L3 技术负责人确认等级；降级需相应负责人留痕。Agent 推荐等级，发现新风险先停止相关实施。
- 用户确认第一版面向 Java 后端、Maven、Spring Boot；精确版本、测试框架、profile 和报告配置未提供。

## 本轮已完成

- 导入并维护单一主设计与实施接力，添加 Agent 指南、ADR 和项目状态。
- 补充操作基线提案、GitLab 手动验收路径、工作电脑验证手册、正负验证案例、公开迁移说明、MR 与验收模板。
- 核验 Spec Kit v1.1.2 / commit 959e866caa3618bf3dc290d5dca33394365af9c6，记录精确来源与本地包版本。
- 在个人电脑隔离环境安装并运行 CLI，生成 generic Skills，安装 Bug 与 Lean，校验官方 bugfix Bundle 清单。
- 虚构 Workflow gate 验证：无 verdict 暂停，提供 approve 恢复完成，reject 终止；这不代表可信人工批准。
- 发现 CLI 1.1.2 无 workflow validate 命令；默认 speckit Workflow 未包含 Converge 和真实测试，应显式执行或后续原生组合。
- 补充 AC-to-Test JSON 0.1、虚构 Spec/映射/XML、Python 标准库检查器与操作说明；不接管原生开发流程。
- 检查器 24 个自检在个人电脑 Python 3.14.8 与 Apple Python 3.9.6 均通过，覆盖正例、缺映射、跳过/失败、缺报告、旧报告、执行非零和被测版本变化等。全部使用虚构报告、模拟命令与临时 Git 仓库，未运行真实 Maven/Spring Boot 工程。

## 阶段状态

| 阶段 | 状态 | 剩余内容 |
|---|---|---|
| T0 环境与原生能力 | 部分完成 | 原生个人电脑核验完成；真实客户端、内部 GitLab 与工作电脑事实待验证 |
| T1 真实最小闭环 | 未完成 | 尚无批准的业务试点与实际 Agent 端到端结果 |
| T2 AC-to-Test | 实验原型完成 | JSON 0.1/默认 Maven XML 检查器与虚构自检通过；真实工程适配及受管环境待验证 |
| T3 交付约束 | 操作设计已补充 | GitLab MR 模板已有；内部权限、人工执行与合并核验未运行 |
| T4 两客户端 | 未验证 | 插件基线、App 版本、实际发现/执行/接力 |
| T5 复杂任务与新工程 | 未验证 | 实际业务试点与样本指标 |
| T6 官方 Bundle | 未实施 | 先验证闭环，再封装稳定且必要的组件 |

## 仍需讨论/收敛

尚待负责人确认的细则：紧急例外的具体审批人/补全期限、试点规模和实际业务 AC。已确认的 MR 路径、分级权限与独立 Review 原则不再重复讨论；具体人员与平台约束能力在工作电脑验证。未回应不等于已批准。

## 下一步

1. 用当前材料进行完整性审查与公开准备；保持主设计和接力说明为入口。
2. 工作电脑先自检检查器，再核验真实 POM/JUnit/报告布局、两个客户端、GitLab 记录/权限和真实业务 AC；必要时最小调整原型，不另建测试平台。
3. 维护公开准备检查，确定发布账号/仓库名/许可证后再发布。
4. 工作电脑按 work-mac-validation.md 收集事实并逐项验证，内部结果不回传公开仓库。

## 验证材料

具体运行结果与固定上游来源见 [原生能力核验](research/native-capability-audit.md) 和 [版本快照](research/version-baseline.json)。本地完整日志及探针在忽略的 work/；不能将其存在视为工作环境通过。
