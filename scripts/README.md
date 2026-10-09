# Maven 验收检查器（实验版）

仅依赖 Python 3.9+ 标准库与本机 Git。不会安装工具、修改 POM、判断人工审批或执行合并。契约与限制见 [验收契约](../docs/acceptance-contract.md)。

开发者日常通过 [L0～L3 Skill 入口](../docs/developer-guide.md)由 Agent 执行检查，无需手动键入下面每条命令。本页用于维护与诊断。唯一检查器实现位于 [team-sdlc Extension](../extensions/team-sdlc/scripts/verify_maven_acceptance.py)，本目录脚本只是兼容启动器；业务工程可直接运行原生安装后的 `.specify/extensions/team-sdlc/scripts/verify_maven_acceptance.py`。

## 在真实工程使用

先由人确认本轮 Spec/AC、风险等级、Maven 实际测试范围与报告布局。在业务工程中复制并调整 [映射样例](../examples/maven-acceptance/acceptance.json)，使用真实 XML 的 classname/name，不猜测测试名称。源码、测试、Spec 和映射应已提交；报告与本地结果目录应被忽略。

在标准仓库根执行下列示例，把路径换成允许的内部位置；输出必须使用一个尚不存在的文件名：

```sh
python3 scripts/verify_maven_acceptance.py \
  --repo /path/to/business-repo \
  --mapping specs/001-change/acceptance.json \
  --output /path/to/internal-evidence/run-001.json \
  -- ./mvnw clean verify
```

命令只是示例：以工程已有入口与批准的 profile 为准。检查器不会自行添加 clean、跳过测试或启用 Failsafe。多模块工程逐项声明需要的报告集合。非默认报告目录、重复测试标识和参数化测试布局须先核验。

退出码 0：当前模式的自动检查通过，仍须人工审核；1：执行/报告/证据检查失败；2：输入、前置条件或工具错误。JSON 结果与同名 .log 文件保存在指定位置。超时视为失败；当前原型不保证终止构建工具派生的全部进程，超时后由执行者确认进程和工作区状态再重试。

默认运行模式要求业务仓库有提交且工作区干净。检查器自身无需安装在业务仓库。结果保存在仓库内时必须已忽略且未跟踪；不会覆盖已有结果或日志。不支持 Git 子模块工程，发现后先记录限制。

## 只读诊断与虚构样例

`--reports-only` 不运行命令、不验证版本和报告新鲜度。它适用于格式探索，不能作为本轮交付证据。以下操作仅在标准仓库忽略的 work/ 生成虚构报告：

```sh
mkdir -p work/maven-demo/target/surefire-reports
cp examples/maven-acceptance/spec.md examples/maven-acceptance/acceptance.json work/maven-demo/
cp examples/maven-acceptance/fixtures/TEST-example.OrderTimeoutTest.xml work/maven-demo/target/surefire-reports/
python3 scripts/verify_maven_acceptance.py \
  --repo work/maven-demo --mapping acceptance.json --reports-only
```

只有映射的两个虚构自动项会显示 passed；execution 为空，freshness 为 unverified，delivery_status 为 requires_review。样例没有 Java 源码，不能证明 Spring Boot 或 Maven 实际执行成功。

## 原型自检

```sh
python3 -m unittest discover -s tests -v
```

测试使用临时 Git 仓库和模拟命令生成 XML，覆盖正常、缺失、跳过、失败、旧报告及版本变化。它验证检查器逻辑，真实 Maven/Spring Boot 工程和两个客户端仍需现场验证。

已安装 Spec Kit 1.1.2 时还会运行两个原生 Extension 生命周期测试（共 26 个测试）；未安装时这两个测试 skip，不应记录成通过。可通过 TEAM_SDLC_SPECIFY 指定批准的 CLI 路径，不自动安装依赖。
