# Spec Kit 原生能力核验

日期：2026-10-10。环境：个人电脑的隔离虚拟环境与虚构项目。未在工作电脑、团队插件、Qoder App 或内部 GitLab 验证。

## 1. 版本基线

- 官方发布：[v1.1.2](https://github.com/github/spec-kit/releases/tag/v1.1.2)，发布时间 2026-10-07T22:27:43Z。
- 核验源码提交：`959e866caa3618bf3dc290d5dca33394365af9c6`。
- 本地安装包：`specify-cli==1.1.2`，`specify --version` 实际输出 `specify 1.1.2`。
- Python：本地成功使用 3.14.8；上游 pyproject 声明要求 >=3.11。
- 组件源版本：Lean 1.0.0、Bug 1.0.0、speckit Workflow 1.0.1、bugfix Workflow 1.0.0。
- 机器可读记录：[version-baseline.json](version-baseline.json)。其中依赖列表是本次观察快照，不是跨平台带哈希锁文件。

上游源码与完整运行日志留在忽略的 work/，不作为公开分发物，也不依赖个人路径。

## 2. 实际核验结果

| 能力 | 结果 | 已验证边界 / 剩余限制 |
|---|---|---|
| CLI 安装与版本 | pass | 在 Python 3.14.8 的隔离环境安装源码并运行；未验证 MDM 环境 |
| generic Skills 初始化 | pass | 空白样例生成 10 个核心 Skill、Constitution、模板、Python/Bash 脚本与原生 Workflow |
| 官方 Bug Extension | pass | `extension add bug` 安装成功，注册 assess/fix/test 三个 Skill；未执行真实 Bug |
| 官方 Lean Preset | pass | `preset add lean` 安装成功，版本 1.0.0；未验证团队任务效果 |
| 官方 bugfix Bundle 清单检查 | pass | `bundle validate --path ... --offline` 校验官方清单通过；不是完整 Bundle 安装/升级验证 |
| Workflow 暂停 | pass | 虚构 gate 在无 TTY 且无 verdict 时返回 paused，未运行后续步骤 |
| Workflow 恢复 | pass | 为虚构探针提供 approve 后返回 completed；不代表真实人工审批 |
| Workflow 拒绝 | pass | 虚构 gate 提供 reject 后返回 aborted、退出码 1 |
| `workflow validate` CLI 命令 | 不存在 | 1.1.2 实际返回 No such command；不能按文档提及直接使用 |
| Converge | 源码/生成入口确认 | 原生命令存在；尚未执行实际一致性分析或代码实现循环 |
| Flow-forward | 官方设计确认 | 团队约定，不是 CLI 设置；未运行真实变更归档 |
| qodercli | 源码确认 | 输出 `.qoder/skills`，声明需要 CLI；不能证明独立 App 能执行 |
| Continue 自研插件 / Qoder App | unverified | 缺少实际版本和客户端条件 |
| GitLab MR / 手动验收 | unverified | 当前只有设计和模板，没有内部权限或业务执行结果 |
| team-sdlc Extension 0.1.1 | 安装/注册 pass | 原生安装注册统一 start 与四级兼容入口，共享参考与检查器随包复制；不是会话行为通过 |
| generic Skills / 命令文件 | 安装/移除 pass | 两种布局均注册五入口，移除后核心文件和历史 Spec 保持不变 |
| 官方 speckit CLI Workflow + generic | 预期受限 | 实际 specify 第一步 failed，无法 CLI 派发；本版用当前 Agent 会话衔接 |

## 3. 安装问题与结论

首次虚拟环境误用了系统 Python 3.9.6，旧安装器首先表现为依赖无法解析；升级隔离环境安装器后明确提示 `specify-cli requires Python >=3.11`。改用 3.14.8 后安装成功。

结论：工作电脑先检查实际解释器，不把包解析失败直接推断为 MDM、网络或 Spec Kit 功能不支持。不要求安装特定的 3.14 版本，满足上游要求且公司允许的版本即可；具体兼容性仍需验证。

## 4. 可复现的最小命令

仅在允许的个人/隔离验证环境使用。下面是验证步骤，不是团队业务工程初始化授权；工作电脑遵循批准的软件源和工具策略。

```sh
python3 --version
# 确认 Python >=3.11，再建立隔离工具环境。
python3 -m venv .venv
.venv/bin/python -m pip install 'git+https://github.com/github/spec-kit.git@959e866caa3618bf3dc290d5dca33394365af9c6'
.venv/bin/specify --version
.venv/bin/specify init work/probe-generic --integration generic --integration-options='--commands-dir .agents/skills --skills' --script py --non-interactive
cd work/probe-generic
../../.venv/bin/specify extension add bug
../../.venv/bin/specify preset add lean
```

本地实际安装使用锁定提交的源码目录，以上 Git URL 为同一提交的可移植来源表达；Git URL 安装方式未在工作电脑测试。上述命令生成工具指令，未调用模型或执行真实需求。

generic 样例生成 `/speckit-specify` 等入口说明。不同客户端的调用语法仍由各自验证，不能把示例 Slash Command 当作所有 App 的统一语法。

### 虚构 gate 的复现

本仓库自写的 [gate-probe 样例](../../examples/gate-probe/workflow.yml) 只有 gate 与输出标记，不调用 Agent、不处理业务数据。仍在 work/probe-generic 中运行：

```sh
../../.venv/bin/specify workflow run ../../examples/gate-probe/workflow.yml --json
```

无交互输入时预期返回 paused，记录 JSON 的 run_id；使用 `workflow resume` 对该 run_id 提供 `--input decision=approve --json`，预期 completed。新运行提供 `--input decision=reject --json`，预期 aborted、退出码 1。实际执行前查看帮助与样例内容；自动提供 verdict 只是虚构控制流测试，不能记录成业务人工审批。

## 5. 原生复用与必要差距

| 需求 | 复用方式 | 必要团队工作 |
|---|---|---|
| 需求、计划、任务、实现 | Core 或 Lean | 精简团队验收字段，人工确认真实语义 |
| Bug 分析与修复验证 | 官方 Bug Extension / bugfix 流程 | 根据风险决定是否适用，不把所有 Bug 归 L0 |
| 人工暂停与恢复 | 原生 Workflow gate | 连接可信 MR 确认记录，不能由本地 verdict 自证授权 |
| 实现后 Converge | 原生命令 | 默认 speckit Workflow 只包含 specify/plan/tasks/implement；Converge 和实际验收需显式调用或后续用原生 overlay 组合 |
| 工具入口 | 现有 integration；必要时 generic | 验证实际客户端，必要时薄适配；不复制指令引擎 |
| AC 与报告追踪 | 现有验收场景和测试报告 | 已补 JSON 0.1/Maven XML 实验检查器；真实工程适配未验证，见 [契约](../acceptance-contract.md) |
| 无自动 CI 验收 | 现有测试命令 + GitLab MR | 手动执行和人工核验，同一契约未来可接 CI |
| 分发 | 官方 Bundle | 试点后组合受支持组件，验证升级/移除及文件归属 |

generic 生成的 taskstoissues 属于 GitHub Issue 同步方向，第一版内部 GitLab 流程不调用它，也不安装 GitHub 专属扩展。Issue/MR 引用先沿用团队现有做法。已有 Git 仓库的分支管理可以继续用原有 Git 操作，原生 git 扩展属于可选能力，不能默认依赖其面向 GitHub 的远程识别。

## 6. 固定版本的主要依据

- [包与 Python 要求](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/pyproject.toml)
- [Flow-forward](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/docs/concepts/spec-persistence.md)
- [generic 实现](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/src/specify_cli/integrations/generic/__init__.py)
- [qodercli 实现](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/src/specify_cli/integrations/qodercli/__init__.py)
- [默认 speckit Workflow](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/workflows/speckit/workflow.yml)
- [Bundle 机制](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/docs/reference/bundles.md)

未将整个上游测试套件作为团队落地验收。当前探针只证明表内范围，工作环境验证按专门手册进行。

## Maven 验收原型的个人电脑验证

2026-10-10：新增 JSON 0.1 映射和标准库检查器。24 个自检在 Python 3.14.8 与 Apple Python 3.9.6 均通过（命令：`python -m unittest discover -s tests -v`，退出码 0）。最初测试夹具未归一化 macOS 临时目录路径别名，已修正夹具并完成上述复跑。

测试仅使用虚构 AC/XML、模拟报告生成命令和临时 Git 仓库，验证映射、失败/跳过、报告缺失/过期、命令失败、干净工作区、提交变化和输出保护。没有运行真实 Maven 构建或 Spring Boot 测试，不表示两个客户端或受管电脑兼容。

实际操作见 [检查器说明](../../scripts/README.md)，设计边界见 [验收契约](../acceptance-contract.md)。不新增第三方 Python 运行依赖。

## 四级可调用入口验证

2026-10-10，0.1.0 首轮：通过 `specify extension add <本地 team-sdlc 目录> --dev` 安装成功并注册四 Skill；`extension info team-sdlc --json` 返回四命令、一脚本。原生生命周期测试覆盖 generic Skills/命令文件两种布局、安装/移除、既有核心文件/Constitution/历史 Spec 保持不变，以及安装内检查器读取虚构报告。

检查器实现迁入 Extension 后，26 个自检在 Python 3.14.8 全部通过，旧启动路径的报告读取示例也通过。新增两项是安装/资源测试，不是模型或客户端行为测试，未执行真实 Maven/Spring Boot 工程。

额外以官方 speckit Workflow 输入虚构描述并选择 generic，实际返回 status=failed、current_step_id=specify、Cannot dispatch command；未调用模型或创建业务实现。来源见固定版本 [command step](https://github.com/github/spec-kit/blob/959e866caa3618bf3dc290d5dca33394365af9c6/src/specify_cli/workflows/step/command/__init__.py)。

原生生成的 Skill 包含 compatibility，skill-creator 的 quick_validate 原样拒绝该字段。四命令源生成的最小 name/description/body 校验副本均通过，仅代表格式检查；没有修改原生受管产物。上游 generic renderer 还固定输出 metadata.author=github-spec-kit，不能据此认定本团队扩展为官方作品。详情见[接入说明](../skill-integration.md)。

## 统一入口与强制风险评估规则补充

2026-10-10：用户明确不能完全依靠开发者自评。team-sdlc 0.1.1 增加 start 统一入口，不要求预选等级；五个入口共用工程证据、规则下限、负责人确认、Plan/实施/diff 复评和最终 Review 复核约定。沿用原生能力和已有 Spec/Mini-Spec 记录，无新评级服务。

修改后重跑两个原生生命周期测试，通过：generic Skills 与命令文件均安装五入口，资源与检查器随包完整，移除保护核心文件/历史 Spec，安装内脚本仍可读取虚构报告。检查器实现未变，本次未重复原有 24 个测试；此前通过记录继续作为既有证据。

风险识别、拒绝低级入口绕过、升降级确认和复评均是新 Skill 行为规则，尚未通过实际模型/客户端验证。对应新增 V2-09～V2-14；不能把安装测试称为评级准确或软件强制门禁。start 命令源的最小 Skill 校验副本通过严格格式校验；上游原样生成产物的 compatibility 字段问题仍保持前述限制。
