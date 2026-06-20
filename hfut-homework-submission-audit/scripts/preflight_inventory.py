#!/usr/bin/env python3
"""Create a read-only inventory for a submission directory or ZIP archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable


CHUNK = 1024 * 1024
IGNORED_DIRS = {".hfut-homework-audit"}
IGNORED_SUFFIXES = {".output", ".errcode"}


def hash_stream(stream: BinaryIO, size: int, max_bytes: int) -> str | None:
    if size > max_bytes:
        return None
    digest = hashlib.sha256()
    while block := stream.read(CHUNK):
        digest.update(block)
    return digest.hexdigest()


def record(path: str, size: int, sha256: str | None, large_bytes: int) -> dict[str, object]:
    suffix = Path(path).suffix.lower()
    flags: list[str] = []
    if size == 0:
        flags.append("empty")
    if size > large_bytes:
        flags.append("large")
    if sha256 is None:
        flags.append("hash_skipped")
    return {"path": path, "bytes": size, "extension": suffix, "sha256": sha256, "flags": flags}


def scan_directory(root: Path, hash_max: int, large_bytes: int) -> tuple[list[dict[str, object]], list[str]]:
    files: list[dict[str, object]] = []
    issues: list[str] = []
    candidates = (
        item
        for item in root.rglob("*")
        if item.is_file()
        and not IGNORED_DIRS.intersection(item.relative_to(root).parts)
        and item.suffix.lower() not in IGNORED_SUFFIXES
    )
    for path in sorted(candidates, key=lambda item: str(item).lower()):
        relative = path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
            with path.open("rb") as stream:
                digest = hash_stream(stream, size, hash_max)
            files.append(record(relative, size, digest, large_bytes))
        except OSError as exc:
            issues.append(f"unreadable:{relative}:{exc}")
    return files, issues


def unsafe_zip_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return path.is_absolute() or ".." in path.parts or (len(normalized) >= 2 and normalized[1] == ":")


def scan_zip(path: Path, hash_max: int, large_bytes: int) -> tuple[list[dict[str, object]], list[str]]:
    files: list[dict[str, object]] = []
    issues: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for info in sorted((item for item in archive.infolist() if not item.is_dir()), key=lambda item: item.filename.lower()):
                flags: list[str] = []
                if unsafe_zip_name(info.filename):
                    flags.append("unsafe_archive_path")
                if info.flag_bits & 0x1:
                    flags.append("encrypted")
                    digest = None
                else:
                    try:
                        with archive.open(info, "r") as stream:
                            digest = hash_stream(stream, info.file_size, hash_max)
                    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                        digest = None
                        flags.append("unreadable")
                        issues.append(f"unreadable:{info.filename}:{exc}")
                item = record(info.filename, info.file_size, digest, large_bytes)
                item["flags"] = sorted(set(item["flags"]) | set(flags))
                files.append(item)
    except zipfile.BadZipFile as exc:
        issues.append(f"invalid_zip:{exc}")
    return files, issues


def summarize(source: Path, files: list[dict[str, object]], issues: Iterable[str]) -> dict[str, object]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for item in files:
        if item["sha256"]:
            by_hash[str(item["sha256"])].append(str(item["path"]))
    duplicates = [paths for paths in by_hash.values() if len(paths) > 1]
    extension_counts = Counter(str(item["extension"]) or "[no extension]" for item in files)
    flag_counts = Counter(flag for item in files for flag in item["flags"])
    return {
        "source": str(source.resolve()),
        "file_count": len(files),
        "total_bytes": sum(int(item["bytes"]) for item in files),
        "extension_counts": dict(sorted(extension_counts.items())),
        "flag_counts": dict(sorted(flag_counts.items())),
        "duplicate_groups": duplicates,
        "issues": list(issues),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--hash-max-mb", type=int, default=100)
    parser.add_argument("--large-file-mb", type=int, default=200)
    args = parser.parse_args()
    if not args.source.exists():
        raise FileNotFoundError(args.source)
    hash_max = args.hash_max_mb * 1024 * 1024
    large_bytes = args.large_file_mb * 1024 * 1024
    if args.source.is_dir():
        files, issues = scan_directory(args.source, hash_max, large_bytes)
    elif args.source.suffix.lower() == ".zip":
        files, issues = scan_zip(args.source, hash_max, large_bytes)
    else:
        raise ValueError("source must be a directory or .zip archive")
    result = summarize(args.source, files, issues)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output.resolve())
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
