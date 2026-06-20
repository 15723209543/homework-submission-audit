# `audit-result.json` 结构

生成脚本接收 UTF-8 JSON：

```json
{
  "task_name": "experiment1",
  "contact": "",
  "students": [
    {"name": "张三", "student_id": "2025000001", "statuses": ["SUCC"]},
    {"name": "李四", "student_id": "2025000002", "statuses": ["NF"]},
    {"name": "王五", "student_id": "2025000003", "statuses": ["101", "301"]}
  ],
  "outsiders": [
    {"name": "名单外提交者", "student_id": "未知", "statuses": ["103"]}
  ],
  "errors": [
    {"category": "个人信息错误", "code": "101", "fix": "修改正文中的学号，确保与班级名单一致。"},
    {"category": "任务完成错误", "code": "301", "fix": "补全缺少的必做题目。"},
    {"category": "个人信息错误", "code": "103", "fix": "核对提交者身份，并确认是否应加入班级名单。"}
  ]
}
```

字段规则：

- `task_name`：可选，默认 `homework`；只用于默认文件名。
- `contact`：可选；为空时不输出联系方式，不得杜撰。
- `students`：必填，按班级名单原顺序排列。
- `outsiders`：可选，追加到 `.output` 最后。
- `name`、`student_id`：按字符串处理。
- `statuses`：只能是单独的 `SUCC`、单独的 `NF`，或一个以上 `[1-6][0-9][0-9]` 错误码。
- `errors`：必须恰好覆盖 `statuses` 中实际引用的全部错误码；代码不可重复。
- 可添加 `evidence`、`source_files`、`confidence` 等字段留存过程证据，生成脚本会忽略它们。

显式指定输出文件名前缀：

```powershell
python scripts/generate_audit_files.py audit-result.json --output-dir final --basename class-report
```

脚本会拒绝无效状态、未定义代码、未使用代码、重复代码、非法文件名和无法编码为 GBK 的文本。
