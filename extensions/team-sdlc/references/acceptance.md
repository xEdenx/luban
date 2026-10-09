# 在入口内执行 Maven 验收

当前实验契约为 acceptance.json 0.1，仅支持显式模块集合与默认 Surefire/Failsafe 报告布局。检查器使用 Python 3.9+ 标准库与 Git，安装位置是业务仓库的 `.specify/extensions/team-sdlc/scripts/verify_maven_acceptance.py`。

Spec 中每个 AC 都必须映射，不能添加 Spec 中不存在的 AC。映射的 spec 路径相对映射文件，module 相对业务仓库根；根模块为 `.`。自动项的 class/name 精确匹配 XML testcase，参数化测试以实际名称为准。先探索实际测试报告再定选择器，完成映射并形成干净提交后重新执行交付验证。

```json
{
  "schema_version": "0.1",
  "change_id": "本轮变更标识",
  "risk_level": "L1",
  "spec": "spec.md",
  "report_sets": [{"module": ".", "kind": "surefire"}],
  "criteria": [{
    "id": "AC-001", "kind": "automated",
    "tests": [{"module": ".", "kind": "surefire", "class": "实际测试类", "name": "实际用例名称"}]
  }]
}
```

人工项使用 `{"id":"AC-002","kind":"manual","reason":"原因","procedure":"可执行步骤"}`，实际执行人/时间/结果保存在内部审核记录中；不能填到自动通过统计。

在业务仓库根，选择未占用的内部输出文件，以工程允许的实际命令运行，例如：

```sh
python3 .specify/extensions/team-sdlc/scripts/verify_maven_acceptance.py \
  --repo . --mapping specs/001-change/acceptance.json \
  --output /path/to/internal-evidence/run-001.json \
  -- ./mvnw clean verify
```

执行前源码、测试、Spec 和映射已提交且工作区干净；报告目录应被忽略。命令不固定为 clean verify，实际 profile/模块选择由工程和确认的验证范围决定。verify 不保证项目已绑定 Failsafe。

结果与同名 .log 保存在内部允许位置，拒绝覆盖。退出码非零、映射缺失、必需测试缺失/跳过/失败、零测试、旧报告或被测版本变化都不能算通过；0 也只意味着当前模式自动检查通过，交付仍 requires_review。reports-only 仅做格式诊断，不证明执行或新鲜度。

不支持定制报告布局与 Git 子模块；超时后要确认残留构建进程。无法运行时记录 blocked/unverified，保留原有测试与人工核验，不伪造检查器通过。Reviewer 还要核对测试断言、模块/profile 覆盖、实际业务功能、人工项和最终 MR 版本。
