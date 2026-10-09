# 工具兼容矩阵

日期：2026-10-10。目标工具：Continue 自研 VS Code 插件、Qoder 独立 Coding Agent App。实际版本均待工作环境采集；当前无客户端通过结论。

| 能力 | Continue 自研插件 | Qoder 独立 App | 工作电脑验证方法 |
|---|---|---|---|
| 规则/AGENTS.md 加载 | unverified | unverified | 新会话显式读取并确认实际作用域 |
| 原生 Skill/命令发现 | unverified | unverified | 查 UI/加载记录，再调用小样例 |
| generic 产物导入/引用 | unverified | unverified | 选择允许的文件入口，区分自动发现与手动引用 |
| 辅助脚本与相对路径 | unverified | unverified | 正确工作区中运行无风险样例 |
| 人工确认与恢复 | unverified | unverified | 未确认时暂停，恢复后继续正确版本 |
| 调用原生 Workflow | unverified | unverified | 验证实际 launcher，不假设 Skills 支持即支持 headless CLI |
| 执行项目已有测试 | unverified | unverified | 保存完整结果、退出码与报告 |
| 分支/活跃 Spec 定位 | unverified | unverified | 切换变更后不读取旧记录为当前意图 |
| 跨工具接力 | unverified | unverified | 只用仓库产物续做同一变更 |
| 安装/升级/移除 | unverified | unverified | 检查受管文件与项目定制保护 |

## 候选入口与依据

Continue 上游文档提供 [Rules](https://docs.continue.dev/customize/deep-dives/rules) 和 [Prompts](https://docs.continue.dev/customize/deep-dives/prompts)。自研分支是否保留这些机制需要源码与实际 UI 验证。

Qoder 独立产品有 [App 概述](https://docs.qoder.com/qoder/overview) 与 [Skills 文档](https://docs.qoder.com/qoder/skills)。实际产品版本、导入格式和项目作用域仍待验证；不要使用 QoderWork 或 IDE/CLI 的结果替代。

Spec Kit generic Skills 产物已在个人电脑生成；qodercli 源码表明其输出 `.qoder/skills` 并需要 CLI。这两个事实均不足以证明独立 App 集成通过。

## 结果分类

- native：该真实客户端可发现并正确执行原生入口，实际验证通过。
- thin-adapter：需要小入口适配，产物与流程逻辑仍使用 Spec Kit。
- manual-reference：只能人工引用指令文件，仍可试验流程，不能计为自动集成。
- blocked：缺少允许的依赖、权限或功能，记录原因。
- unverified：未执行。

每项结果关联工具版本、材料版本和内部证据。不要将所有“能读取 Markdown”的客户端笼统认定为支持同一 Skills 机制。
