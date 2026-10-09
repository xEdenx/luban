# Agent 工作约定

本仓库维护团队 Agent-Native Development 标准与必要扩展，不是业务应用，也不是新的 Spec 引擎。

先读 README.md、docs/memory.md、docs/technical-design.md；实际实施按 docs/implementation-handoff.md。架构决策记录在 docs/adr/。

- 继承 Spec Kit 1.x、Flow-forward、L0–L3、AC-to-Test、AGENTS.md + Skills + CI、后续官方 Bundle 的路线。
- 优先官方原生能力，其次配置、薄适配，最后必要扩展。不复制原生 Spec 工作流，不建立中央编排器。
- 团队使用自部署 GitLab，当前无法自动触发 CI。第一版以人工运行现有验证命令、版本绑定的验收证据和人工合并审核闭环；不能声称已启用自动 CI 门禁。手动流水线、Runner 和审批功能待核验。
- Continue 自研 VS Code 插件、Qoder 独立 Coding Agent App 分别验证；CLI、IDE、App 与上游/自研分支不可混同。
- 已确认 L1 单 MR 分阶段；L2 单 MR 分阶段并确认技术方案；L3 Spec MR + 实现 MR。先确认具体版本再实现，最终交付通常由另一位开发者审核，特殊情况记录例外。
- Agent 推荐等级；L0/L1 由模块负责人确认，L2/L3 由技术负责人确认。发现新风险先停止相关实施并上报，降级需相应负责人留痕。
- 第一版适配 Java 后端、Maven、Spring Boot；最小 AC 检查器采用 Python 标准库与 acceptance.json。实际 JUnit/插件版本和真实报告布局待验证。
- 区分官方资料支持、本地已验证、团队环境已验证、未验证。记录实际版本、命令和结果，不用文件存在或模型自评替代运行证据。
- 历史 Spec 仅作历史。本轮范围、AC 或关键设计修改需重新人工确认。当前进行公开设计、原生探针与最小验收原型验证，尚未授权未确认的业务实现。
- work/ 存临时上游源码、探针、运行日志；.venv/ 为隔离工具环境。不要修改全局工具配置或覆盖既有项目文件。
- 工程材料发布前同步技术设计、项目记忆和必要 ADR。复用现有文件，避免重复的主设计或状态系统。
- 不把受控合并等同于阻止本地代码生成；不把人工核验称为不可绕过的机器门禁。
- 验证按影响范围执行；文档检查链接与结构，工具验证记录正例和关键失败条件。未配置远程，不自行推送或发布。
