#!/usr/bin/env python3
"""从各插件的 GitHub 最新 release 同步版本号到 index.json。

用法: python sync_versions.py [index.json]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# 匹配 repo 字段里的 owner/repo（支持带/不带 https、末尾斜杠、.git）
_REPO_RE = re.compile(r"(?:https?://github\.com/)?([^/\s]+/[^/\s]+?)(?:\.git)?/?$", re.IGNORECASE)


def repo_slug(repo_url: str) -> str | None:
    """从 repo URL 提取 owner/repo。"""
    m = _REPO_RE.match(repo_url.strip())
    return m.group(1) if m else None


def latest_tag(slug: str) -> str | None:
    """用 gh CLI 取最新 release 的 tag（含 v 前缀），失败返回 None。"""
    try:
        out = subprocess.run(
            ["gh", "release", "view", "-R", slug, "--json", "tagName", "--jq", ".tagName"],
            check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    tag = out.stdout.strip()
    return tag or None


def strip_v(tag: str) -> str:
    return tag[1:] if tag.startswith("v") else tag


def dumps_inline_arrays(plugins: list, indent: int = 2) -> str:
    """序列化为 JSON，保持 tags 等字符串数组内联，与手工维护格式一致。

    等价于 json.dumps(ensure_ascii=False, indent=2)，但短字符串数组输出为
    ["a", "b"] 而非多行展开，从而最小化 diff。
    """
    sep = " " * indent
    lines = ["["]
    for i, p in enumerate(plugins):
        lines.append(f"{sep}{{")
        items = list(p.items())
        for j, (k, v) in enumerate(items):
            comma = "," if j < len(items) - 1 else ""
            if isinstance(v, list) and all(isinstance(x, str) for x in v):
                arr = ", ".join(json.dumps(x, ensure_ascii=False) for x in v)
                lines.append(f'{sep * 2}"{k}": [{arr}]{comma}')
            else:
                lines.append(f'{sep * 2}{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}')
        lines.append(f"{sep}}}{',' if i < len(plugins) - 1 else ''}")
    lines.append("]")
    return "\n".join(lines) + "\n"


def main(index_path: str = "index.json") -> int:
    path = Path(index_path)
    plugins = json.loads(path.read_text(encoding="utf-8"))

    changed = False
    for p in plugins:
        pid = p.get("id", "?")
        slug = repo_slug(p.get("repo", ""))
        if not slug:
            print(f"::warning::{pid}: invalid repo url: {p.get('repo')}")
            continue

        tag = latest_tag(slug)
        if not tag:
            print(f"::warning::{pid}: no release found for {slug}")
            continue

        new_ver = strip_v(tag)
        old_ver = p.get("version", "")
        if new_ver == old_ver:
            print(f"{pid}: v{old_ver} (current)")
            continue

        print(f"{pid}: v{old_ver} -> v{new_ver}")
        p["version"] = new_ver
        p["path"] = f"releases/download/v{new_ver}/aq-{pid}.zip"
        changed = True

    if changed:
        path.write_text(dumps_inline_arrays(plugins), encoding="utf-8")
        print("index.json updated")
    else:
        print("All up to date")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "index.json"))
