# 维护者：Spec Kit 统一入口与四级路径的接入与验证

日期：2026-10-10。组件：team-sdlc Extension 0.1.1；当前只锁定并核验 Spec Kit 1.1.2。它是团队扩展，不是 GitHub/OpenAI 官方开发方法。公开发布的仓库地址与许可证尚未确定，清单未伪填这些信息。

开发者日常只需[选择入口并提供需求](developer-guide.md)。本页是工程维护者的一次性接入和诊断说明，不要求每位开发者每项任务重做安装。

## 1. 封装了什么

[Extension 清单](../extensions/team-sdlc/extension.yml)声明五个原生命令：日常默认 start，其余是兼容路径建议，由 Spec Kit 对当前 integration 注册：

| 原生命令（保持原样） | 对外入口 Skill（本仓库 skills/ 提供） | 行为 |
|---|---|---|
| speckit.team-sdlc.start | eden-team-speckit-start/SKILL.md | 无需预先评级，工程风险评估后走 L0～L3 路径 |
| speckit.team-sdlc.l0 | eden-team-speckit-l0/SKILL.md | Mini-Spec 确认后最小修复/验证 |
| speckit.team-sdlc.l1 | eden-team-speckit-l1/SKILL.md | Spec/AC 确认后自动规划、编码、测试 |
| speckit.team-sdlc.l2 | eden-team-speckit-l2/SKILL.md | 增加技术方案确认和影响面验证 |
| speckit.team-sdlc.l3 | eden-team-speckit-l3/SKILL.md | 已批准且合入 Spec 基线后开展实现 MR |

对外入口统一采用 eden-team-speckit-start / l0～l3，源文件见 [skills/](../skills)。它们只读取业务仓库安装内的 commands/{mode}.md 并执行，继续使用原有共享规则。Spec Kit 原生注册/生成名称、Extension 清单与版本、命令文件和执行流程保持原样，不增命令别名、不改上游生成器。

命令源只指定输入模式，五个入口共用[执行约定](../extensions/team-sdlc/references/flow.md)。Specify/Clarify/Plan/Tasks/Analyze/Implement/Converge 继续使用工程实际安装并生效的原生指令；没有复制原生引擎或模板。

Extension 同时携带验收参考和唯一一份 Maven 检查器实现。标准仓库原有 scripts/verify_maven_acceptance.py 保留为兼容启动入口；业务工程直接调用安装内脚本，不依赖个人电脑路径或标准仓库之外的文件。

## 2. 首次安装：先隔离试验

使用公司允许的 Python、Spec Kit 和软件来源。CLI 安装要求 Python >=3.11，检查器单独运行要求 Python >=3.9 与 Git。Spec Kit 安装来源与锁定提交见[核验记录](research/native-capability-audit.md)。

以下命令已按本机 CLI 帮助和实际探针验证；specify 应指向已批准的 1.1.2 环境。替换路径，在尚不存在的空白目录试验：

```sh
specify --version
specify init /path/to/new-sandbox --integration generic \
  --integration-options='--commands-dir .agents/skills --skills' \
  --script py --non-interactive
cd /path/to/new-sandbox
specify extension add /path/to/luban/extensions/team-sdlc --dev
specify extension info team-sdlc --json
# 仅限本节刚初始化的新样例，五个目标目录尚不存在：
cp -R /path/to/luban/skills/eden-team-speckit-* .agents/skills/
```

最后一步只是复制团队薄 Skill。目标使用实际客户端已验证的项目 Skills 目录，本例为 .agents/skills；目录已存在时先比较版本与本地修改，不直接覆盖。原生生成的 speckit-team-sdlc-* 内部入口保留，开发者选择 eden-team-speckit-* 对外入口。

Extension 的 add/info 是官方本地开发安装方式，当前没有发布可用的扩展 URL/目录或 Bundle。验证期间保留标准仓库源目录，不把开发安装称作已经完成正式安装/升级策略。

既有业务工程先检查是否已初始化、当前 integration/模板覆盖与未提交修改；在隔离分支/副本审查 diff 后接入，不直接在原工程套用 init 或 --force。

若客户端只支持命令文件，可在另一空白样例把 integration-options 改为 `--commands-dir .agent-commands`，不带 --skills。安装后会生成 `speckit.team-sdlc.l1.md` 等文件。这也只是文件产物，仍须在真实客户端验证发现与执行。

## 3. 必须保留的依赖

- 当前 integration 下的统一入口、四个兼容入口及原生 Spec Kit 指令。
- 薄 Skill 读取的 `.specify/extensions/team-sdlc/commands/`，以及 `references/` 与 `scripts/`，由原生安装复制管理。
- `.specify/` 原有模板/脚本/Constitution，以及工程规范和真实构建入口。

不能只复制五个 SKILL.md 就宣布安装完成。入口会读取业务仓库内的共享规则；App 若把导入包隔离到其他位置，必须验证能否正确读取工程文件，必要时再做薄适配。

## 4. 在客户端验证一次调用

在 Continue 自研插件和 Qoder 独立 App 分别进行：

1. 发现/显式引用 start 统一入口，输入虚构需求文档或变化描述。
2. 检查 Agent 真正读取当前规范/代码，先给出风险证据和建议等级，再调用原生能力生成所需 Spec；等级不能来自开发者自报。
3. 人工确认前不得实施业务代码；提出一处业务修订，检查同一活跃 Spec 被修订并重新展示。
4. 由正确角色确认具体版本后，检查 Agent 自动继续 Plan/Tasks/Implement/Converge 和实际验证，不再要求人逐条调用命令。
5. 检查交付证据、功能核对步骤与 MR 草稿；未验证项不能自动变成通过。
6. 补显式 L0 输入权限修复仍识别 L3、风险未知不按 L0 开工、实施影响面扩大复评、无有效记录降级被拒、L2 方案确认、L3 缺合入基线和跨工具继续等案例。

角色/审核身份依赖实际项目配置与可信记录。本地入口不是权限系统，无法单独证明确认人的身份、强制合并门禁或本地代码生成时间。

## 5. CLI Workflow 与会话 Skill 的边界

Spec Kit 1.1.2 的 Workflow command 步骤通过 integration CLI 派发。个人电脑已用官方 speckit Workflow + generic 验证：第一步返回 failed，提示无法派发 speckit.specify。因此本版由当前 Agent 会话衔接原生指令，不把 generic 误称为 CLI 自动执行通道。

以后真实工具支持相应 CLI 时，再评估原生 Workflow/overlay。Qoder CLI 的结果不能代表 Qoder App；Continue 上游的结果不能代表自研插件。

## 6. 已验证与未验证

已验证原生安装、五入口注册、Skills/命令文件两种布局、共享资源/检查器随包安装、移除不改既有核心文件与历史 Spec，以及检查器原有失败条件。详情见[核验记录](research/native-capability-audit.md)。未验证真实模型驱动的需求到交付、客户端 UI、内部 GitLab 和 Spring Boot 工程。

五个对外薄 Skill 源文件均通过 skill-creator 的严格格式检查；这不代表实际模型/客户端执行成功。

skill-creator 的严格 quick_validate 不接受上游生成的 compatibility 字段；原样校验会失败。0.1.0 时只对由四个命令源生成的最小 Skill 校验副本验证 name/description/body（通过），没有改写原生受管文件，也不把副本通过称为客户端兼容。

上游 generic renderer 固定生成 metadata.author=github-spec-kit；它不是本扩展作者或官方背书。实际扩展清单 author 为 team-sdlc contributors，source 为 extension:team-sdlc。不要依赖该 renderer 默认值判定归属。

## 7. 回退与后续分发

先保留工程 Git 快照；不再试点时通过原生 `specify extension remove team-sdlc` 移除，并审查 diff。手工复制的五个 eden-team-speckit-* 薄 Skill 不归原生安装器管理；停止使用时，维护者应核对具体目录、归属与本地修改后单独移除，保留其他 Skills，不使用通配删除。仅承诺本次隔离测试范围内的核心/历史文件保护，不保证升级原子性。不要手工删除整个 .specify/。

行为验证通过后再决定稳定版本、许可证与发布来源，未来由官方 Bundle 组合本扩展和确有必要的 Preset/Workflow。当前不追加自建启动器、审批服务或 CI 服务。
