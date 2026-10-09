# Maven AC-to-Test 验收契约 0.1

状态：可验证的实验实现，尚未在真实 Spring Boot 工程、受管工作电脑或内部 GitLab 验证。用户已确认第一版面向 Java 后端、Maven 构建、Spring Boot；未指定 JUnit、Spring Boot 或 Maven 插件的实际版本。

## 1. 原生能力与最小扩展

Spec Kit 原生 spec.md 已包含用户场景、验收场景和需求。沿用这些内容，每个验收场景加稳定 ID；不另写一份业务需求，不复制 Specify/Plan/Tasks/Implement。

本次只补三项：稳定 AC ID、引用 AC 的机器映射、读取 Maven XML 报告与记录实际执行的检查器。命令由开发者明确指定，通常使用项目已有的 `./mvnw verify` 或既有 profile；不修改 POM、不安装 JDK/Maven、不推断生产权限。

现由 team-sdlc 入口中的 Agent 根据工程已有验证配置准备并执行命令；人工发起/确认工作流不意味着必须人工键入命令。检查器唯一实现随原生 Extension 安装，旧 scripts 路径仅作兼容入口。

机器映射采用 acceptance.json，以便 Python 标准库直接读取。主设计早期 acceptance.yaml 是提案，当前实验实现只支持 JSON，不同时维护两套格式。这是工程格式选择，不增加业务审批步骤。

## 2. Spec 中的 AC 标识

在原生 Acceptance Scenarios 的有序/无序条目中添加粗体 ID，例如：

```markdown
**Acceptance Scenarios**:

1. **AC-001**: **Given** 未支付订单达到已确认的到期时刻，**When** 执行取消任务，**Then** 订单被取消。
2. **AC-002**: **Given** 订单已支付，**When** 执行取消任务，**Then** 保持已支付状态。
```

ID 在本次变更内唯一，跨变更使用 change_id + AC ID。当前检查器只提取这种条目，忽略代码围栏中的示例，不解析整个 Markdown 或替代业务审查。零 AC、重复 ID、缺映射、多余映射都失败。

## 3. 最小映射字段

示例见 [完整虚构样例](../examples/maven-acceptance/acceptance.json)。

| 字段 | 含义与约束 |
|---|---|
| schema_version | 当前为字符串 0.1 |
| change_id / risk_level | 变更身份与 L0–L3；字段存在不表示人工已确认等级 |
| spec | 相对映射文件的 spec.md 路径，必须位于被测仓库内 |
| report_sets | 明确需要收集的模块和 surefire/failsafe 报告集合；不能凭空认为整个 reactor 都被覆盖 |
| criteria[].id | 对应 Spec 中唯一 AC |
| criteria[].kind | automated 或 manual |
| automated.tests[] | 精确的 module、kind、class、name，匹配实际 XML testcase |
| manual.reason / procedure | 需要人工验证的原因与步骤；结果留在内部审核记录 |

module 是相对仓库根的模块路径，根模块用 `.`。一个 AC 可要求多个测试，全部通过才算自动验证通过。禁止模糊匹配；参数化/动态测试先按实际报告的名称逐项列出，出现重复或歧义时检查失败，由现场核验后再扩展。

## 4. 执行与证据

运行方式见 [操作说明](../scripts/README.md)。默认模式要求干净且已有提交的业务仓库；先记录代码提交、Spec/映射摘要和报告状态，再执行用户明确给出的命令，最后核对工作区、提交、摘要与新报告。

结果与日志写到仓库外，或仓库内已忽略且未跟踪的位置；拒绝覆盖已有结果。日志可能含内部信息，只留内部批准位置。输出中保留命令、退出码、报告文件摘要、逐 AC 结果和未完成的人工项。

当前报告新鲜度要求：消费的报告是本次新增或更新，且文件时间落在执行窗口内。已有旧报告、不执行测试或遗留报告混入会失败。文件时间/摘要可发现常见误用，不能证明不可伪造；本地证据仍依赖执行身份、独立 Reviewer 和必要复跑。

检查器比较执行前后的提交、Git 工作区状态及 Spec/映射摘要；能发现保留在工作区的源码、测试、POM 或配置变更，不能证明执行期间没有修改后又恢复的内容。测试之后变化需要重新执行相关验证。输出日志/报告必须位于忽略位置，不能混入源码状态判断。首版不支持 Git 子模块工程。

## 5. 判定规则

| 情况 | 自动结果 |
|---|---|
| Maven 命令非零退出，即使 XML 全通过 | failed |
| 必需报告集合不存在、无 testcase 或 XML 不可读 | failed |
| AC 缺映射、重复、映射找不到唯一 testcase | failed |
| 映射测试 skipped / failure / error | failed |
| 收集范围内任意 testcase 失败或出现失败重试/不稳定标记 | failed，需明确处理后重跑 |
| 默认运行模式消费旧报告、被测提交/源码变化 | failed |
| 自动项通过但有人工项 | 自动项 passed，交付仍 requires_review |
| 纯报告读取模式 | 只判断给定报告；来源、版本和新鲜度为 unverified |

纯报告模式供虚构样例、历史格式探索和诊断使用，不能替代默认运行模式的执行证据。退出码 0 只表示该模式的自动检查通过，不表示人工确认、整个工程覆盖或允许合并。

未映射的 skipped 测试会单独统计，交给 Reviewer 判断是否违反已确认验证范围；不能用 skipped 满足必需 AC。实际 JUnit 版本、插件配置、禁用测试方式、参数化测试名称仍要在工作电脑验证。

## 6. Maven 的核验依据与边界

Surefire 默认产生 target/surefire-reports/TEST-*.xml；Failsafe 默认产生 target/failsafe-reports/TEST-*.xml，并在 integration-test/verify 阶段执行。验收使用实际 testcase，不把 failsafe-summary.xml 当作逐测试结果。[Surefire 官方说明](https://maven.apache.org/surefire/maven-surefire-plugin/)、[Failsafe 官方说明](https://maven.apache.org/surefire/maven-failsafe-plugin/)

项目配置可以改变目录、profile、执行范围或插件绑定。本版只支持上述默认报告布局与显式模块集合；定制布局发现后据实标记不支持，不猜测为通过。verify 并不保证项目已经绑定 Failsafe，也不保证所有集成测试已运行。

## 7. 当前不负责的事情

不提供新测试框架、Spring Boot 项目模板、CI 服务、审批签名服务、GitLab 机器人或多 Agent 编排。检查器不会确认 Spec 的业务语义，不会自行认可人工验收、发布授权和风险降级。第三方工具兼容性仍按工作电脑手册验证。
