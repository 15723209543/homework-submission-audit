#!/usr/bin/env python3
"""Generate aligned GBK .output and .errcode files from an audit JSON."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


CODE_RE = re.compile(r"^[1-6][0-9]{2}$")
SAFE_BASENAME_RE = re.compile(r"^[^<>:\"/\\|?*\x00-\x1f]+$")


def width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in {"W", "F"} else 1 for ch in value)


def pad(value: str, target: int) -> str:
    return value + " " * (target - width(value))


def table(headers: list[str], rows: list[list[str]]) -> str:
    all_rows = [headers, *rows]
    widths = [max(width(row[index]) for row in all_rows) for index in range(len(headers))]
    return "\n".join("    ".join(pad(cell, widths[index]) for index, cell in enumerate(row)).rstrip() for row in all_rows)


def text(value: Any, field: str) -> str:
    if value is None:
        raise ValueError(f"{field} cannot be null")
    rendered = str(value).strip()
    if not rendered:
        raise ValueError(f"{field} cannot be empty")
    if "\n" in rendered or "\r" in rendered:
        raise ValueError(f"{field} cannot contain newlines")
    return rendered


def normalize_person(raw: dict[str, Any], field: str) -> dict[str, Any]:
    name = text(raw.get("name"), f"{field}.name")
    student_id = text(raw.get("student_id"), f"{field}.student_id")
    statuses_raw = raw.get("statuses")
    if not isinstance(statuses_raw, list) or not statuses_raw:
        raise ValueError(f"{field}.statuses must be a non-empty list")
    statuses = [text(item, f"{field}.statuses") for item in statuses_raw]
    if len(statuses) != len(set(statuses)):
        raise ValueError(f"{field}.statuses contains duplicate values")
    if statuses in (["SUCC"], ["NF"]):
        pass
    elif all(CODE_RE.fullmatch(item) for item in statuses):
        statuses = sorted(statuses, key=int)
    else:
        raise ValueError(f"{field}.statuses must be only SUCC, only NF, or 1xx-6xx codes")
    return {"name": name, "student_id": student_id, "statuses": statuses}


def normalize(data: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, str]]]:
    task_name = str(data.get("task_name", "homework")).strip() or "homework"
    basename = task_name
    students_raw = data.get("students")
    if not isinstance(students_raw, list):
        raise ValueError("students must be a list")
    people = [normalize_person(item, f"students[{index}]") for index, item in enumerate(students_raw)]
    outsiders_raw = data.get("outsiders", [])
    if not isinstance(outsiders_raw, list):
        raise ValueError("outsiders must be a list")
    people.extend(normalize_person(item, f"outsiders[{index}]") for index, item in enumerate(outsiders_raw))

    extra_checks_raw = data.get("extra_checks", [])
    if not isinstance(extra_checks_raw, list):
        raise ValueError("extra_checks must be a list")
    failed_custom_codes: set[str] = set()
    for index, item in enumerate(extra_checks_raw):
        text(item.get("requirement"), f"extra_checks[{index}].requirement")
        result = text(item.get("result"), f"extra_checks[{index}].result")
        if result not in {"pass", "fail", "not_checked"}:
            raise ValueError(f"extra_checks[{index}].result must be pass, fail, or not_checked")
        code_value = item.get("code")
        if result == "fail":
            code = text(code_value, f"extra_checks[{index}].code")
            if not re.fullmatch(r"^6[0-9]{2}$", code):
                raise ValueError(f"extra_checks[{index}].code must be a 6xx code")
            if code in failed_custom_codes:
                raise ValueError(f"duplicate failed extra-check code: {code}")
            failed_custom_codes.add(code)
        elif code_value not in (None, ""):
            raise ValueError(f"extra_checks[{index}] may only include code when result is fail")
        if result == "not_checked":
            text(item.get("reason"), f"extra_checks[{index}].reason")

    errors_raw = data.get("errors", [])
    if not isinstance(errors_raw, list):
        raise ValueError("errors must be a list")
    errors: list[dict[str, str]] = []
    defined: set[str] = set()
    for index, item in enumerate(errors_raw):
        category = text(item.get("category"), f"errors[{index}].category")
        code = text(item.get("code"), f"errors[{index}].code")
        fix = text(item.get("fix"), f"errors[{index}].fix")
        if not CODE_RE.fullmatch(code):
            raise ValueError(f"errors[{index}].code must match [1-6][0-9][0-9]")
        if code in defined:
            raise ValueError(f"duplicate error definition: {code}")
        defined.add(code)
        errors.append({"category": category, "code": code, "fix": fix})

    used = {status for person in people for status in person["statuses"] if CODE_RE.fullmatch(status)}
    missing = sorted(used - defined)
    unused = sorted(defined - used)
    if missing:
        raise ValueError(f"undefined error code(s): {', '.join(missing)}")
    if unused:
        raise ValueError(f"unused error definition(s): {', '.join(unused)}")
    used_custom_codes = {code for code in used if code.startswith("6")}
    if used_custom_codes != failed_custom_codes:
        missing_checks = sorted(used_custom_codes - failed_custom_codes)
        missing_usage = sorted(failed_custom_codes - used_custom_codes)
        details = []
        if missing_checks:
            details.append(f"6xx code(s) without failed extra_checks entry: {', '.join(missing_checks)}")
        if missing_usage:
            details.append(f"failed extra-check code(s) not used in student statuses: {', '.join(missing_usage)}")
        raise ValueError("invalid 6xx interface (" + "; ".join(details) + ")")
    return basename, people, sorted(errors, key=lambda item: int(item["code"]))


def output_header(filename: str) -> list[str]:
    return [
        f"# 文件名称：{filename}",
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


def errcode_header(filename: str) -> list[str]:
    return [
        f"# 文件名称：{filename}",
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


def write_gbk(path: Path, content: str) -> None:
    try:
        encoded = content.encode("gbk", errors="strict")
    except UnicodeEncodeError as exc:
        bad = content[exc.start : exc.end]
        raise ValueError(f"text contains characters not encodable as GBK near {bad!r}") from exc
    path.write_bytes(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 audit-result.json")
    parser.add_argument("--output-dir", type=Path, required=True, help="User-designated task folder for final files")
    parser.add_argument("--basename", help="Output filename stem; defaults to task_name")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing final files after explicit user approval")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("input JSON root must be an object")
    default_basename, people, errors = normalize(data)
    basename = (args.basename or default_basename).strip()
    if not basename or not SAFE_BASENAME_RE.fullmatch(basename) or basename in {".", ".."}:
        raise ValueError("basename contains invalid filename characters")

    if not args.output_dir.exists() or not args.output_dir.is_dir():
        raise ValueError("output-dir must be an existing user-designated task folder")
    output_path = args.output_dir / f"{basename}.output"
    errcode_path = args.output_dir / f"{basename}.errcode"
    existing = [path for path in (output_path, errcode_path) if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError("refusing to overwrite existing final file(s): " + ", ".join(str(path) for path in existing))

    output_rows = [[person["name"], person["student_id"], " ".join(person["statuses"])] for person in people]
    error_rows = [[item["category"], item["code"], item["fix"]] for item in errors]
    output_content = "\n".join(output_header(output_path.name)) + "\n\n" + table(["姓名", "学号", "提交情况"], output_rows) + "\n"
    errcode_content = "\n".join(errcode_header(errcode_path.name)) + "\n\n" + table(["错误码分类", "错误码", "应该如何修改"], error_rows) + "\n"
    write_gbk(output_path, output_content)
    write_gbk(errcode_path, errcode_content)
    print(output_path.resolve())
    print(errcode_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
