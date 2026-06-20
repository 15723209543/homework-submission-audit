---
name: hfut-homework-submission-audit
description: Perform high-alert audits of class homework, lab reports, course projects, and group submissions stored together in a user-designated folder, even when that folder is not the current working directory; read all inputs from that folder, write the final GBK .output and .errcode back into the same folder, match submitters, surface evidence-based concerns, assign dynamic 1xx-5xx warnings plus 6xx codes for failed user-added checks. Use when the user says “使用 $HFUT-homework-submission-audit 检查这批班级作业。” or invokes $hfut-homework-submission-audit, and for 班级作业检查、NF/SUCC 汇总、格式内容异常、AI/相似性风险预警、错误码生成。
---

# HFUT 班级作业提交检查

执行高预警、可复核的班级作业初筛。主动提出所有有证据支持的可疑点，不把示例当作问题上限；同时不得捏造问题，不把风险提示写成成绩、作弊或 AI 使用的最终认定。

## 调用约定

将以下中文句子视为调用本 Skill 的明确指令：

```text
使用 $HFUT-homework-submission-audit 检查这批班级作业。
```

内部合法标识为 `$hfut-homework-submission-audit`。两种大小写写法都按本工作流处理。

## 输入

要求用户把本次任务的对应文件放在同一个资料文件夹中。优先取得：

1. 班级名单，至少含姓名和学号。
2. 作业要求及模板，含命名、格式、必交内容和特殊规则。
3. 班级提交物，可为目录或压缩包。
4. 用户本次额外提出的检查任务；没有则使用空清单。

缺少材料时先完成仍可确定的项目，明确未检查范围；无法读取的压缩包不能据此把学生判为 `NF`。开始检查前读取 [references/audit-spec.md](references/audit-spec.md)，生成结果前读取 [references/result-schema.md](references/result-schema.md)。

## 资料文件夹与输出位置

首先确定用户资料文件夹的绝对路径并记为 `TASK_DIR`：

1. 优先使用用户明确给出的文件夹路径。
2. 其次使用用户附加文件或当前选中材料共同所在的文件夹。
3. 若材料分散但存在明确的共同任务父目录，使用该父目录。
4. 若无法唯一确定，不得退回当前工作目录；先询问用户资料文件夹路径。

检查 `TASK_DIR` 存在、可读且可写。若文件夹位于当前工作区之外或权限受限，向用户申请访问权限后继续。不要把文件复制到当前目录来规避路径或权限问题。

所有输入从 `TASK_DIR` 读取。中间文件放在资料文件夹内的专用子目录，最终结果直接放在资料文件夹根目录：

```text
<TASK_DIR>/
  班级名单及作业材料...
  <任务名>.output
  <任务名>.errcode
  .hfut-homework-audit/
  inventory.json
  extracted/
  evidence/
  audit-result.json
```

不要修改学生原文件，也不要在 Skill 目录或当前工作目录写任务产物。安全解压，拒绝路径穿越。默认不执行学生提交的程序、宏或脚本；必须执行时使用隔离、最小权限和超时。

## 工作流

### 1. 建立检查清单

把作业要求拆成可验证条目。再把用户额外提出的每项检查任务原样登记到 `extra_checks`，分配稳定 ID。额外检查未通过时必须从 `601` 起动态分配 `6xx`；不得把用户额外要求混入 1xx-5xx，也不得把系统自行发现的常规问题滥用为 6xx。

### 2. 盘点提交物

定位本 Skill 的绝对目录并运行：

```powershell
python <skill-dir>/scripts/preflight_inventory.py <TASK_DIR> --output <TASK_DIR>/.hfut-homework-audit/inventory.json
```

检查空文件、重复文件、异常体积、加密或损坏 ZIP、不安全归档路径、扩展名异常和重复版本。对不支持的 `.7z`、`.rar` 使用环境中可用的只读工具；没有工具时记录未检查范围。

### 3. 规范化名单并匹配

保留名单原顺序，把学号按字符串处理并保留前导零。按证据强度匹配：正文/可靠元数据中的完整学号 > 文件名完整学号 > 姓名学号联合匹配 > 仅姓名弱匹配。

- 没有可归属提交：`NF`。
- 名单外提交：追加到 `.output` 最后。
- 多人一组、代交、重名、学号冲突或多版本不明：保留歧义并预警，不强行归属。
- `SUCC`、`NF` 和错误码互斥；存在任何错误码时不得输出 `SUCC`。

### 4. 执行高预警检查

不要只检查规范中的示例。逐文件、逐要求扫描任何可能影响完整性、可读性、归属、真实性、可复现性或评分公平性的异常。对每个有合理依据的问题记录文件路径、页码/单元格/代码位置、对应要求、观察事实、置信度和人工复核建议。

- `1xx`：个人信息、身份、归属或文件名/正文冲突。
- `2xx`：文件类型、命名、结构、排版、模板或呈现格式不符。
- `3xx`：必做内容、过程、数据、截图、结果、分析、引用或结论缺失。
- `4xx`：AI 或跨提交相似性风险；只能作为风险提示。
- `5xx`：损坏、空文件、加密、编码、体积、扩展名、恶意内容或版本异常。
- `6xx`：仅用于用户本次额外提出的检查任务未通过。

采用“有问题就预警、证据不足就标明不确定性”的原则。不要为了提高预警率虚构错误；合理疑点可以登记错误码并写明“建议人工复核”。同一问题影响多人时复用同一码，不同问题必须使用不同代码。

### 5. 谨慎处理 AI 与相似性

不要声称测得可靠“AI 率”，也不要只凭文风判定。只有存在多个独立风险信号时才登记 4xx。跨提交相似性必须排除题目原文、公共模板、教师材料、正确答案中的必然相同部分和常见代码骨架，并保留可定位证据。

### 6. 生成与校验

按 [references/result-schema.md](references/result-schema.md) 写 UTF-8 `audit-result.json`，再运行：

```powershell
python <skill-dir>/scripts/generate_audit_files.py <TASK_DIR>/.hfut-homework-audit/audit-result.json --output-dir <TASK_DIR>
python <skill-dir>/scripts/validate_audit_files.py <TASK_DIR>/<名称>.output <TASK_DIR>/<名称>.errcode
```

`--output-dir` 必须显式传入 `TASK_DIR`，不得省略或改用当前目录。若同名结果已经存在，默认换用清晰的新名称；只有用户明确同意覆盖时才加 `--overwrite`。必须修复所有校验错误再交付。最终文件头必须与 `assets/example.output`、`assets/example.errcode` 一致，文件名行按实际文件名替换；两个文件均使用严格 GBK 编码。

## 交付

只交付 `TASK_DIR` 根目录中的最终 `.output`、`.errcode` 和用户明确要求的报告，并返回它们的绝对路径。简短汇总名单人数、已提交、`NF`、各类预警、名单外提交、6xx 自定义检查结果和未检查范围。对 4xx 与低置信度问题明确标注“风险提示，需人工复核”。
