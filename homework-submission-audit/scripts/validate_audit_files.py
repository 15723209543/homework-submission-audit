#!/usr/bin/env python3
"""Validate GBK audit output files and cross-check referenced error codes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CODE_RE = re.compile(r"^[1-6][0-9]{2}$")


def read_gbk(path: Path) -> str:
    raw = path.read_bytes()
    try:
        content = raw.decode("gbk", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} is not strict GBK: {exc}") from exc
    if "# 文件编码：GBK" not in content:
        raise ValueError(f"{path} is missing the GBK header")
    return content


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
