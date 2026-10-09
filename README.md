# Agent-Native SDLC

以 GitHub Spec Kit 原生能力为基础，采用 Flow-forward、L0–L3 与 AC-to-Test，逐步形成可推广的团队研发标准。

当前：仓库已初始化，已完成部分原生能力核验和 Maven AC-to-Test 实验原型；尚未接入业务工程或完成两个客户端验证。

当前在个人电脑准备完整方案，后续公开 GitHub 分发通用材料，在受 MDM 管控的工作 MacBook 按手册验证。公开发布尚未执行。

## 阅读入口

- [主技术设计](docs/technical-design.md)：已决策路线、生命周期、风险分级和验收设计。
- [实施任务接力](docs/implementation-handoff.md)：T0–T6 的依赖、操作与验收条件。
- [项目记忆](docs/memory.md)：事实、当前进度、待确认事项和下一步。
- [原生能力核验](docs/research/native-capability-audit.md)：锁定版本、运行结果与最小差距。
- [工具兼容矩阵](docs/research/tool-compatibility.md)：Continue 自研插件与 Qoder 独立 App。
- [ADR-0001](docs/adr/0001-native-first-flow-forward.md)：原生优先与生命周期决策。
- [ADR-0002](docs/adr/0002-gitlab-manual-verification.md)：无自动 CI 触发时的第一版交付路径。
- [ADR-0003](docs/adr/0003-maven-acceptance-prototype.md)：最小 Maven 验收原型的取舍与边界。
- [团队操作基线](docs/team-operating-profile.md)：已确认的审批路径、风险负责人及待批准细则。
- [Maven 验收契约](docs/acceptance-contract.md)与[检查器操作说明](scripts/README.md)：最小映射、手动运行及限制。
- [GitLab 手动验收路径](docs/gitlab-manual-verification.md)：无自动流水线时如何形成可复核证据。
- [工作电脑验证手册](docs/work-mac-validation.md)：材料获取、环境预检、真实客户端与业务试点。
- [验证案例](docs/validation-cases.md)：正例、负例和实际约束边界。
- [公开发布与迁移](docs/public-release.md)：公开/内部边界、版本与工作电脑接力。

## 可复用模板

[验收记录](templates/verification-record.md)、[工作电脑验证结果](templates/workstation-validation-record.md) 和 [.gitlab/merge_request_templates](.gitlab/merge_request_templates) 下的 MR 模板可作为起点。模板没有预填通过结论，也不是强制门禁。

## 已知团队环境

团队使用自部署 GitLab，无法自动触发 CI。第一版采用“人工运行已有测试 → 生成绑定代码版本的证据 → GitLab Merge Request 人工审核”的路径。是否能手动触发流水线、是否有 Runner、能否强制审批/保护分支仍待核验。

不以引入 Spec Kit 为由更换 Git 平台、测试框架或客户端；CI 保持为架构能力，当前落地强度据实记录。

## 仓库边界

尚无团队 Preset、Extension 或 Bundle。已补一个必要的 AC 映射/报告检查原型；它不编排开发流程、不承担 CI 或审批服务。先验证再封装。work/ 与 .venv/ 为忽略的临时研究环境，不能当作正式分发物。
