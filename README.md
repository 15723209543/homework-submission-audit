# HFUT Homework Submission Audit Skill

> 一个用于批量检查班级作业提交情况的 Codex / AI Skill。  
> 支持根据班级名单、作业要求与模板、学生提交文件，生成 GBK 编码的 `.output` 和 `.errcode` 检查结果文件。

## 1. Skill 简介

`hfut-homework-submission-audit` 是一个面向班级作业、实验报告、课程设计、小组报告等批量提交场景的 AI Skill。

它可以辅助完成：

- 班级名单与提交文件匹配
- 未提交学生检查
- 个人信息一致性检查
- 作业格式与模板检查
- 作业完成情况检查
- AI 或相似性风险提示
- 文件异常检查
- 用户额外任务要求检查
- 动态错误码生成
- GBK 编码 `.output` / `.errcode` 文件输出

本 Skill 的定位是**高预警、可复核、辅助初筛**。  
它不会把风险提示写成最终成绩、作弊结论或 AI 使用结论。

---

## 2. 适用场景

适合使用本 Skill 的情况包括：

- 班级作业批量检查
- 实验报告提交情况核对
- 课程设计报告初步筛查
- 小组作业提交整理
- 学生提交文件命名检查
- 学号、姓名、正文信息匹配
- 缺交学生 `NF` 汇总
- 无明显问题学生 `SUCC` 汇总
- 按错误码输出问题学生
- 对名单外提交者进行记录
- 对用户额外提出的检查要求进行记录

不建议将本 Skill 的输出结果直接作为最终成绩或最终违规认定依据。

---

## 3. 可行性分析

本 Skill 已经完成两次班级作业检查实战，能够在真实提交材料中完成名单匹配、错误码登记、问题汇总和结果文件输出，具备继续使用和迭代优化的基础。

截至目前，实际检查战绩如下：

- 累计查获 **14 项个人信息错误** 的作业。
- 查获 **6 项不符合要求** 的作业。
- 向 **27 人次同学** 发出预警。

从两次实战结果来看，本 Skill 在“批量初筛”场景中具有较高实用价值。它可以快速定位未提交、个人信息错误、格式不规范、任务完成不完整等常见问题，减少人工逐份打开文件检查的重复劳动，也能让检查结果以 `.output` 和 `.errcode` 的形式统一保存，便于后续复核、反馈和归档。

同时，本 Skill 的输出定位仍然是辅助检查。除是否提交外，其他结果仍需人工复核，尤其是 AI 风险、相似性风险、格式细节和任务完成度等判断，不应直接作为最终成绩或最终违规认定依据。

---

## 4. 可优化方向

后续可以从以下方向继续优化：

1. **增强文件解析能力**  
   进一步提升对 Word、PDF、Excel、图片型 PDF、混合压缩包等文件的解析效果，减少因格式复杂导致的误判或漏判。

2. **优化模板比对能力**  
   支持更细粒度地识别模板结构、章节标题、表格内容、必填区域和附件要求，让格式错误与任务完成错误的区分更加准确。

3. **完善相似性检查机制**  
   在相似性分析前自动排除题目原文、课程模板、教师提供的公共内容和常见固定表述，减少把正常相似内容误判为抄袭风险的情况。

4. **改进 AI 风险提示逻辑**  
   继续坚持“不输出确定性 AI 率、不直接认定 AI 生成”的原则，转向输出更可复核的风险信号，例如语言风格突变、事实冲突、异常结构重复等。

5. **支持更多压缩包格式**  
   当前脚本原生支持目录和 `.zip`，后续可以增强对 `.7z`、`.rar` 等格式的兼容能力，并对无法解析的压缩包给出更清晰的未检查范围说明。

6. **增加统计汇总报告**  
   在 `.output` 和 `.errcode` 之外，增加一个可选的统计报告，例如已提交人数、未提交人数、各类错误码数量、名单外提交者数量、未检查文件数量等。

7. **加强证据记录能力**  
   对每一个错误码记录对应证据来源，例如文件名、页码、章节、截图位置或文本片段，方便人工复核时快速定位问题。

8. **扩展代码类作业检查**  
   对程序设计、数据结构、算法实验等代码类作业，可以增加编译检查、运行检查、超时检查、输出格式检查等可选模块，并使用 6 开头错误码记录额外任务结果。

9. **优化交互式使用体验**  
   后续可让 Skill 在信息不足时主动询问缺失材料，例如班级名单、模板、命名规则、是否允许多人一组、是否检查代码、是否检查附件等。

10. **提高结果可移植性**  
    除 GBK 编码的 `.output` 和 `.errcode` 外，可额外生成 UTF-8 的 JSON、CSV 或 Markdown 汇总文件，便于跨平台查看和二次处理。

---

## 5. Skill 标识

Skill 内部名称：

```text
hfut-homework-submission-audit
```

推荐调用方式：

```text
使用 $HFUT-homework-submission-audit 检查这批班级作业。
```

规范标识：

```text
$hfut-homework-submission-audit
```

大小写写法均可理解为调用本 Skill。

---

## 6. 安装方法

### 6.1 Windows 安装

将 `hfut-homework-submission-audit-skill.zip` 发送给使用者，让对方在 PowerShell 中进入压缩包所在目录后运行：

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills"

Expand-Archive ".\hfut-homework-submission-audit-skill.zip" "$HOME\.codex\skills" -Force
```

安装完成后，应存在：

```text
C:\Users\用户名\.codex\skills\hfut-homework-submission-audit\SKILL.md
```

如果出现双层同名目录，例如：

```text
C:\Users\用户名\.codex\skills\hfut-homework-submission-audit\hfut-homework-submission-audit\SKILL.md
```

说明解压层级错误。需要把里面那一层 `hfut-homework-submission-audit` 移到：

```text
C:\Users\用户名\.codex\skills\hfut-homework-submission-audit
```

然后重启 Codex 或新建对话。

### 6.2 macOS / Linux 安装

把压缩包放到当前目录后运行：

```bash
mkdir -p ~/.codex/skills

unzip hfut-homework-submission-audit-skill.zip -d ~/.codex/skills
```

安装完成后，应存在：

```text
~/.codex/skills/hfut-homework-submission-audit/SKILL.md
```

如果出现双层同名目录，需要调整为：

```text
~/.codex/skills/hfut-homework-submission-audit/SKILL.md
```

然后重启 Codex 或新建对话。

### 6.3 从 GitHub 仓库安装

如果通过 GitHub 仓库发布，可以直接克隆到 Codex skills 目录。

macOS / Linux：

```bash
mkdir -p ~/.codex/skills

git clone https://github.com/15723209543/homework-submission-audit ~/.codex/skills/hfut-homework-submission-audit
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills"

git clone https://github.com/15723209543/homework-submission-audit "$HOME\.codex\skills\hfut-homework-submission-audit"
```

安装后确认存在：

```text
hfut-homework-submission-audit/SKILL.md
```

---

## 7. 调用方式

安装完成并重启 Codex 后，可以在新对话中这样调用：

```text
使用 $HFUT-homework-submission-audit 检查这批班级作业。

班级名单是：……
作业要求和模板是：……
学生作业在：……

请生成 GBK 编码的 .output 和 .errcode 文件。
```

更完整的调用示例：

```text
使用 $HFUT-homework-submission-audit 检查这批班级作业。

输入信息：
1. 班级名单：class_list.xlsx
2. 作业要求和模板：homework_template.docx
3. 学生提交作业：submissions.zip

检查要求：
1. 检查名单中每位学生是否提交，未提交返回 NF。
2. 检查提交文件中的姓名、学号是否与名单匹配。
3. 检查文档格式是否符合模板。
4. 检查任务完成情况，多写不算错，少写才算错。
5. 检查 AI 风险和提交文件之间的相似风险。
6. 检查文件异常情况。
7. 如果本次还有其他额外检查要求，使用 6 开头错误码。

输出要求：
1. 生成 GBK 编码的 .output 文件。
2. 生成 GBK 编码的 .errcode 文件。
3. .output 每个学生一行：姓名 + 学号 + 提交情况。
4. .errcode 每个错误码一行：错误码分类 + 错误码 + 应该如何修改。
5. 除是否提交外，其余检查结果仅供参考，最终以人工复核为准。
```

---

## 8. 输入文件要求

本 Skill 通常需要三类输入材料。

### 8.1 班级名单

班级名单至少应包含：

- 姓名
- 学号

建议格式：

- `.xlsx`
- `.xls`
- `.csv`
- `.txt`

处理原则：

- 学号按字符串处理。
- 保留学号前导零。
- 姓名和学号以名单原文为准。
- 不擅自改名。
- 如果出现重名、重复学号、空字段，应提示人工复核。

### 8.2 作业要求及模板

作业要求和模板建议包含：

- 作业题目
- 提交格式
- 文件命名规则
- 文档模板
- 必填内容
- 必做题目
- 截图、代码、附件等额外材料要求
- 用户本次额外提出的检查要求

检查原则：

- 多写的内容一般不算错。
- 少写、漏写模板或题目要求的必要内容才算问题。
- 如果作业要求和模板冲突，应记录冲突并提示人工确认。

### 8.3 学生提交文件

提交文件可以是：

- 一个提交目录
- `.zip` 压缩包
- 其他压缩包格式

当前脚本 `preflight_inventory.py` 原生支持：

- 目录
- `.zip`

对于 `.7z`、`.rar` 等格式，应使用当前环境可用的只读解包工具。  
如果无法解析压缩包，应明确记录未检查范围，不能直接把压缩包内学生判为 `NF`。

---

## 9. 输出文件要求

本 Skill 输出两个主要文件：

```text
<任务名>.output
<任务名>.errcode
```

文件名不固定，可以根据实际任务命名，例如：

```text
experiment1.output
experiment1.errcode
```

或：

```text
程序设计作业.output
程序设计作业.errcode
```

不建议把文件名固定写成某一次任务名，例如 `test1.output`。

---

## 10. `.output` 文件说明

`.output` 文件用于输出每位学生的提交情况。

文件要求：

- 文本文件
- 严格 GBK 编码
- Windows 记事本可打开
- 文件开头为 `#` 开头的说明
- 后续每位学生一行
- 按班级名单原顺序输出
- 名单外提交者放在最后
- 各列按照最大字符宽度制表对齐

格式：

```text
姓名    学号    提交情况
```

提交情况说明：

| 返回值 | 含义 |
|---|---|
| `SUCC` | 已提交，且未发现明显问题 |
| `NF` | 名单中有该学生，但未找到提交文件 |
| `1xx-6xx` | 已提交，但存在对应问题 |

规则：

- `SUCC`、`NF` 与错误码互斥。
- 同一学生有多个问题时，错误码之间使用空格分隔。
- 只要存在错误码，就不要同时写 `SUCC`。
- `NF` 不与任何其他状态同时出现。
- 除是否提交外，其余检查结果仅供参考，最终以人工复核为准。

示例：

```text
# 文件名称：自定义文件名.output
# 文件编码：GBK
# 文件说明：本文件用于输出班级作业提交检查结果。
# 输出格式：姓名 + 学号 + 提交情况
# 提交情况说明：SUCC 表示检查通过；NF 表示未提交；其他三位数字表示对应错误码。
# 如果一名学生存在多个问题，错误码之间使用空格分隔。
# 如果出现班级名单中不存在的提交者，应输出在文件最后。
# 错误码不是固定死的，实际检查时按照现场发现的问题动态申请，并同步写入 .errcode 文件。
# 重要说明：除是否提交外，本文件中的其他检查结果均为辅助判断结果，仅供参考，不作为最终认定依据。
# 免责声明：最终结果应以教师、助教、课程负责人或人工复核结果为准，文件生成者不对使用本结果产生的后果负责。
# 问题反馈方式：https://github.com/15723209543/homework-submission-audit

姓名        学号            提交情况
张三        2025000001      SUCC
李四        2025000002      NF
王五        2025000003      101 301
名单外提交  未知            103
```

---

## 11. `.errcode` 文件说明

`.errcode` 文件用于输出本次检查实际使用的错误码、错误类型和修改建议。

文件要求：

- 文本文件
- 严格 GBK 编码
- Windows 记事本可打开
- 文件开头为 `#` 开头的说明
- 每一个实际使用的错误码一行
- 不提前输出未使用错误码
- 各列按照最大字符宽度制表对齐

格式：

```text
错误码分类    错误码    应该如何修改
```

规则：

- `.errcode` 必须覆盖 `.output` 中实际引用的全部错误码。
- `.errcode` 不应包含 `.output` 中没有使用的错误码。
- 同一个错误码只能定义一次。
- 修改建议必须具体、可执行。
- `4xx` 只写风险提示和人工复核建议，不写定罪式表述。
- 错误码解释和修改建议仅供参考，最终以人工复核为准。

示例：

```text
# 文件名称：自定义文件名.errcode
# 文件编码：GBK
# 文件说明：本文件用于说明作业检查过程中出现的错误码含义及修改建议。
# 输出格式：错误码分类 + 错误码 + 应该如何修改
# 错误码规则：1 开头表示个人信息错误；2 开头表示格式错误；3 开头表示任务完成错误；4 开头表示 AI 或抄袭风险；5 开头表示文件异常。
# 其他检查任务说明：6 开头表示用户本次额外提出的检查任务错误。
# 特别说明：错误码为现场申请，不提前固定全部情况；检查过程中发现新的具体问题时，应申请新的错误码，并在本文件中登记。
# 重要说明：本文件中的错误码解释和修改建议均为辅助判断结果，仅供参考，不作为最终成绩评定或最终违规认定依据。
# 免责声明：最终结果应以教师、助教、课程负责人或人工复核结果为准，文件生成者不对使用本结果产生的后果负责。
# 问题反馈方式：https://github.com/15723209543/homework-submission-audit

错误码分类        错误码      应该如何修改
个人信息错误      101        修改正文中的学号，确保与班级名单一致。
任务完成错误      301        补全缺少的必做题目。
其他任务需求错误  601        补交用户额外要求的附件说明文件。
```

---

## 12. 错误码规则

错误码统一使用三位数字表示：

```text
[1-6][0-9][0-9]
```

错误码不是固定死的，实际检查时按照现场发现的问题动态申请和登记。  
本 Skill 只规定错误码大类，不提前限制具体错误码数量。

| 错误码 | 分类 | 说明 |
|---|---|---|
| `1xx` | 个人信息错误 | 姓名、学号、班级、身份归属、文件名与正文冲突等 |
| `2xx` | 格式错误 | 文件类型、命名、模板、章节、页面、字体、图表、附件位置等 |
| `3xx` | 任务完成错误 | 必做题、过程、数据、代码、测试、截图、结果、分析、引用、结论等缺失 |
| `4xx` | AI 或抄袭风险 | AI 风险信号、排除公共部分后的相似内容或相似代码 |
| `5xx` | 文件异常 | 损坏、为空、加密、编码、体积、扩展名伪装、宏、路径、版本等异常 |
| `6xx` | 其他任务需求错误 | 用户本次额外提出的检查任务未通过 |

### 12.1 `6xx` 说明

`6xx` 专门用于用户本次额外提出的检查任务，例如：

- 必须提交指定声明
- 必须提交源代码说明
- 必须提交演示视频
- 必须包含指定截图
- 必须按照特殊文件夹层级整理
- 必须满足用户临时提出的统计、排序、分类或汇总要求

规则：

1. 用户额外要求应先登记到 `extra_checks`。
2. 额外要求通过时不分配错误码。
3. 额外要求未通过时，从 `601` 起动态分配错误码。
4. 无法检查时标记为 `not_checked` 并说明原因。
5. `6xx` 的修改建议必须直接对应用户原始要求。

---

## 13. 目录结构

本 Skill 的目录结构如下：

```text
hfut-homework-submission-audit/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── audit-result.example.json
│   ├── example.output
│   └── example.errcode
├── references/
│   ├── audit-spec.md
│   └── result-schema.md
└── scripts/
    ├── preflight_inventory.py
    ├── generate_audit_files.py
    └── validate_audit_files.py
```

文件说明：

| 文件 | 作用 |
|---|---|
| `SKILL.md` | Skill 主说明文件，定义触发场景、工作流程和检查原则 |
| `agents/openai.yaml` | Skill 显示名称、简短描述和默认提示 |
| `assets/audit-result.example.json` | 结构化检查结果 JSON 示例 |
| `assets/example.output` | `.output` 文件头和格式示例 |
| `assets/example.errcode` | `.errcode` 文件头和格式示例 |
| `references/audit-spec.md` | 作业检查规范 |
| `references/result-schema.md` | `audit-result.json` 数据结构说明 |
| `scripts/preflight_inventory.py` | 盘点提交目录或 ZIP 文件 |
| `scripts/generate_audit_files.py` | 根据 `audit-result.json` 生成 `.output` 和 `.errcode` |
| `scripts/validate_audit_files.py` | 校验输出文件格式、编码和错误码引用关系 |

---

## 14. 脚本使用说明

### 14.1 盘点提交文件

```bash
python <skill-dir>/scripts/preflight_inventory.py <TASK_DIR> --output <TASK_DIR>/.hfut-homework-audit/inventory.json
```

该脚本用于检查：

- 文件数量
- 文件大小
- 扩展名分布
- 空文件
- 大文件
- 重复文件
- 加密 ZIP
- 损坏 ZIP
- 不安全归档路径
- 无法读取文件

### 14.2 生成 `.output` 和 `.errcode`

先根据检查结果生成 UTF-8 编码的 `audit-result.json`，再运行：

```bash
python <skill-dir>/scripts/generate_audit_files.py <TASK_DIR>/.hfut-homework-audit/audit-result.json --output-dir <TASK_DIR>
```

如需指定输出文件名前缀：

```bash
python <skill-dir>/scripts/generate_audit_files.py <TASK_DIR>/.hfut-homework-audit/audit-result.json --output-dir <TASK_DIR> --basename class-report
```

会生成：

```text
class-report.output
class-report.errcode
```

同名结果默认拒绝覆盖。只有明确需要覆盖时才使用：

```bash
--overwrite
```

### 14.3 校验输出文件

```bash
python <skill-dir>/scripts/validate_audit_files.py <TASK_DIR>/<名称>.output <TASK_DIR>/<名称>.errcode
```

校验内容包括：

- 文件是否为严格 GBK 编码
- 文件头是否符合要求
- `.output` 是否为三列
- `.errcode` 是否为三列
- 错误码是否合法
- `.output` 中使用的错误码是否全部在 `.errcode` 中定义
- `.errcode` 中是否存在未使用错误码
- 是否存在重复错误码

必须修复全部校验错误后再交付结果文件。

---

## 15. 推荐工作流程

建议按以下流程使用：

1. 将班级名单、作业要求、模板、学生提交文件放在同一个资料文件夹。
2. 调用 `$HFUT-homework-submission-audit`。
3. 明确资料文件夹路径。
4. 读取 `references/audit-spec.md`。
5. 运行 `preflight_inventory.py` 盘点提交物。
6. 规范化班级名单。
7. 按学号、姓名、正文信息匹配提交者。
8. 检查个人信息、格式、任务完成情况、AI/相似性风险、文件异常。
9. 对用户额外要求使用 `6xx` 错误码。
10. 生成 `.hfut-homework-audit/audit-result.json`。
11. 运行 `generate_audit_files.py`。
12. 运行 `validate_audit_files.py`。
13. 将最终 `.output` 和 `.errcode` 写回资料文件夹根目录。
14. 向用户简短汇总已提交、未提交、错误码数量、名单外提交和未检查范围。

---

## 16. AI 与抄袭风险边界

本 Skill 只做风险提示，不做最终认定。

### 16.1 AI 风险

不应输出确定性“AI 率”。

不应仅凭以下因素判断 AI：

- 语言流畅
- 表达正式
- 结构清晰
- 词汇丰富
- 主观直觉

只有存在多个独立、可描述、可复核的风险信号时，才建议登记 `4xx`。

推荐表述：

```text
存在 AI 风险信号，建议人工复核。
```

不推荐表述：

```text
该学生使用了 AI。
该文档 AI 率为 xx%。
该作业确定为 AI 生成。
```

### 16.2 相似或抄袭风险

检查相似性时，应先排除：

- 题目原文
- 课程模板
- 教师提供的公共内容
- 公共代码骨架
- 常见短语
- 合理引用内容

只有排除公共部分后，仍存在大段同序文本、相同罕见错误、相同异常结构或高度一致的非模板代码时，才建议登记 `4xx`。

---

## 17. 安全边界

本 Skill 默认只做静态读取和检查，不执行学生提交的程序、宏或脚本。

安全要求：

1. 保留学生原始提交物，不直接修改原文件。
2. 解压文件时拒绝路径穿越。
3. 不执行未知代码。
4. 不运行 Office 宏。
5. 不运行未知脚本。
6. 如用户明确要求运行代码，应在隔离环境、超时限制和最小权限下进行。
7. 对无法读取、损坏、加密或不支持的文件，应记录为异常或未检查范围，不伪装成已完成检查。

---

## 18. 重要说明与免责声明

本 Skill 输出结果主要用于辅助整理和初步筛查班级作业提交情况。

除“是否提交”这一类可以直接依据文件检索结果判断的信息外，其余检查结果均仅供参考，包括但不限于：

- 个人信息匹配
- 格式判断
- 任务完成情况
- AI 风险提示
- 相似性风险提示
- 文件异常判断
- 其他特殊任务判断

本 Skill 不保证所有判断结果完全准确，也不对因使用本 Skill 输出结果而产生的任何后果负责。

最终认定结果应以教师、助教、课程负责人或人工复核结果为准。

---

## 19. 问题反馈

问题反馈方式：

```text
https://github.com/15723209543/homework-submission-audit
15723209543@163.com
```

