#!/usr/bin/env python3
"""Validate GBK audit output files and cross-check referenced error codes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CODE_RE = re.compile(r"^[1-6][0-9]{2}$")

OUTPUT_HEADER_TAIL = [
    "# 文件编码：GBK",
    "# 文件说明：本文件用于输出班级作业提交检查结果。",
    "# 输出格式：姓名 + 学号 + 提交情况",
    "# 提交情况说明：SUCC 表示检查通过；NF 表示未提交；其他三位数字表示对应错误码。",
    "# 如果一名学生存在多个问题，错误码之间使用空格分隔。",
    "# 如果出现班级名单中不存在的提交者，应输出在文件最后。",
    "# 错误码不是固定死的，实际检查时按照现场发现的问题动态申请，并同步写入 .errcode 文件。",
    "# 重要说明：除是否提交外，本文件中的其他检查结果均为辅助判断结果，仅供参考，不作为最终认定依据。",
    "# 免责声明：最终结果应以教师、助教、课程负责人或人工复核结果为准，文件生成者不对使用本结果产生的后果负责。",
    "# 问题反馈方式：https://github.com/15723209543/homework-submission-audit",
]

ERRCODE_HEADER_TAIL = [
    "# 文件编码：GBK",
    "# 文件说明：本文件用于说明作业检查过程中出现的错误码含义及修改建议。",
    "# 输出格式：错误码分类 + 错误码 + 应该如何修改",
    "# 错误码规则：1 开头表示个人信息错误；2 开头表示格式错误；3 开头表示任务完成错误；4 开头表示 AI 或抄袭风险；5 开头表示文件异常。",
    "# 其他检查任务说明：6 开头表示用户本次额外提出的检查任务错误。",
    "# 特别说明：错误码为现场申请，不提前固定全部情况；检查过程中发现新的具体问题时，应申请新的错误码，并在本文件中登记。",
    "# 重要说明：本文件中的错误码解释和修改建议均为辅助判断结果，仅供参考，不作为最终成绩评定或最终违规认定依据。",
    "# 免责声明：最终结果应以教师、助教、课程负责人或人工复核结果为准，文件生成者不对使用本结果产生的后果负责。",
    "# 问题反馈方式：https://github.com/15723209543/homework-submission-audit",
]


def read_gbk(path: Path) -> str:
    raw = path.read_bytes()
    try:
        content = raw.decode("gbk", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} is not strict GBK: {exc}") from exc
    if "# 文件编码：GBK" not in content:
        raise ValueError(f"{path} is missing the GBK header")
    return content


def validate_header(path: Path, content: str, tail: list[str]) -> None:
    expected = [f"# 文件名称：{path.name}", *tail]
    actual = content.splitlines()[: len(expected)]
    if actual != expected:
        for index, (wanted, found) in enumerate(zip(expected, actual), start=1):
            if wanted != found:
                raise ValueError(f"{path} header line {index} mismatch: expected {wanted!r}, got {found!r}")
        raise ValueError(f"{path} header is incomplete")


def data_lines(content: str, header_first_cell: str) -> list[str]:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith(header_first_cell):
            return [item.strip() for item in lines[index + 1 :] if item.strip()]
    raise ValueError(f"table header starting with {header_first_cell!r} not found")


def split_columns(line: str) -> list[str]:
    return [item.strip() for item in re.split(r"\s{2,}", line.strip()) if item.strip()]


def validate(output_path: Path, errcode_path: Path) -> tuple[int, int, set[str]]:
    output = read_gbk(output_path)
    errcode = read_gbk(errcode_path)
    validate_header(output_path, output, OUTPUT_HEADER_TAIL)
    validate_header(errcode_path, errcode, ERRCODE_HEADER_TAIL)
    used: set[str] = set()
    output_rows = data_lines(output, "姓名")
    for row_number, line in enumerate(output_rows, start=1):
        columns = split_columns(line)
        if len(columns) != 3:
            raise ValueError(f"output row {row_number} must have 3 columns: {line!r}")
        statuses = columns[2].split()
        if statuses in (["SUCC"], ["NF"]):
            continue
        if not statuses or not all(CODE_RE.fullmatch(item) for item in statuses):
            raise ValueError(f"output row {row_number} has invalid status: {columns[2]!r}")
        if len(statuses) != len(set(statuses)):
            raise ValueError(f"output row {row_number} repeats an error code")
        used.update(statuses)

    defined: set[str] = set()
    err_rows = data_lines(errcode, "错误码分类")
    for row_number, line in enumerate(err_rows, start=1):
        columns = split_columns(line)
        if len(columns) != 3:
            raise ValueError(f"errcode row {row_number} must have 3 columns: {line!r}")
        code = columns[1]
        if not CODE_RE.fullmatch(code):
            raise ValueError(f"errcode row {row_number} has invalid code: {code!r}")
        if code in defined:
            raise ValueError(f"errcode file repeats code {code}")
        defined.add(code)

    if used != defined:
        missing = sorted(used - defined)
        unused = sorted(defined - used)
        details = []
        if missing:
            details.append(f"undefined: {', '.join(missing)}")
        if unused:
            details.append(f"unused: {', '.join(unused)}")
        raise ValueError("error-code mismatch (" + "; ".join(details) + ")")
    return len(output_rows), len(err_rows), used


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("errcode", type=Path)
    args = parser.parse_args()
    rows, errors, codes = validate(args.output, args.errcode)
    print(f"OK: {rows} submission row(s), {errors} error definition(s), codes={','.join(sorted(codes)) or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
