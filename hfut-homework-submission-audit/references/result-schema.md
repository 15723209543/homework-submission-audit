# `audit-result.json` 结构

生成器接收 UTF-8 JSON：

```json
{
  "task_name": "experiment1",
  "students": [
    {"name": "张三", "student_id": "2025000001", "statuses": ["SUCC"]},
    {"name": "李四", "student_id": "2025000002", "statuses": ["NF"]},
    {"name": "王五", "student_id": "2025000003", "statuses": ["101", "301", "601"]}
  ],
  "outsiders": [],
  "extra_checks": [
    {"requirement": "必须提交源代码说明文件", "result": "fail", "code": "601"}
  ],
  "errors": [
    {"category": "个人信息错误", "code": "101", "fix": "修改正文中的学号，确保与班级名单一致。"},
    {"category": "任务完成错误", "code": "301", "fix": "补全缺少的必做题目。"},
    {"category": "其他任务需求错误", "code": "601", "fix": "补交用户要求的源代码说明文件。"}
  ]
}
```

规则：

- `task_name`：可选，默认 `homework`，用作默认文件名前缀。
- `students`：必填，按名单原顺序。
- `outsiders`：可选，追加到 `.output` 最后。
- `statuses`：只能是单独 `SUCC`、单独 `NF`，或一个以上 `[1-6][0-9][0-9]`。
- `errors`：必须恰好覆盖所有实际引用代码，不能包含未使用定义。
- `extra_checks`：用户自定义检查接口，可为空数组。
- `extra_checks[].requirement`：用户额外检查要求。
- `extra_checks[].result`：只允许 `pass`、`fail`、`not_checked`。
- `fail` 必须有 `6xx` 的 `code`，且该代码必须在学生状态和 `errors` 中使用及定义。
- `pass` 和 `not_checked` 不得携带错误码；`not_checked` 应另加 `reason`。
- 可添加 `evidence`、`source_files`、`confidence` 等字段，生成脚本忽略这些扩展字段。

生成命令：

```powershell
python <skill-dir>/scripts/generate_audit_files.py <TASK_DIR>/.hfut-homework-audit/audit-result.json --output-dir <TASK_DIR> --basename class-report
```

`--output-dir` 必须显式提供并指向已存在的用户资料文件夹 `TASK_DIR`。同名结果默认拒绝覆盖；只有用户明确同意时才使用 `--overwrite`。脚本会拒绝非法状态、未定义/未使用/重复代码、不合法 6xx 接口、非法文件名及无法编码为 GBK 的文本。
