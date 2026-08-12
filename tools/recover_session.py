#!/usr/bin/env python3
"""Find and extract content from local Claude Code session transcripts.

Claude Code writes every session to ~/.claude/projects/<path-slug>/<uuid>.jsonl.
This recovers work from a session you can no longer open interactively.

    # 1. locate transcripts mentioning a company
    python3 recover_session.py search 恒运昌 恒昌运

    # 2. extract one to readable markdown + any files it wrote
    python3 recover_session.py extract <path-to.jsonl> --out recovered/

Cross-platform, standard library only. On Windows use `python` instead of `python3`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Tools whose arguments contain full file content worth reconstructing.
WRITE_TOOLS = {"Write", "NotebookEdit", "create_or_update_file"}
EDIT_TOOLS = {"Edit", "MultiEdit"}

# cat > path <<'EOF' ... EOF   /   cat >> path <<EOF ... EOF
HEREDOC = re.compile(
    r"cat\s+>>?\s*(?P<path>[^\s<>|;&]+)\s*<<-?\s*(?P<q>['\"]?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)(?P=q)\s*\n"
    r"(?P<body>.*?)\n(?P=tag)\b",
    re.DOTALL,
)


def default_root() -> Path:
    return Path(os.path.expanduser("~")) / ".claude" / "projects"


def iter_records(path: Path):
    """Yield parsed JSON objects, skipping malformed lines."""
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"  ! skipped malformed line {lineno} in {path.name}", file=sys.stderr)


def blocks_of(rec: dict) -> list:
    """Content blocks for a record, normalising the several shapes they take."""
    msg = rec.get("message")
    content = msg.get("content") if isinstance(msg, dict) else rec.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def record_text(rec: dict) -> str:
    """All human-readable text in a record, for searching."""
    parts = []
    for b in blocks_of(rec):
        t = b.get("type")
        if t in ("text", "thinking"):
            parts.append(str(b.get("text") or b.get("thinking") or ""))
        elif t == "tool_use":
            parts.append(json.dumps(b.get("input", {}), ensure_ascii=False))
        elif t == "tool_result":
            c = b.get("content")
            parts.append(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
    return "\n".join(parts)


def summarise(path: Path) -> dict:
    """Metadata for a transcript without loading it all into memory twice."""
    info = {
        "path": path,
        "session_id": None,
        "cwd": None,
        "branch": None,
        "first_prompt": None,
        "start": None,
        "end": None,
        "records": 0,
    }
    for rec in iter_records(path):
        info["records"] += 1
        info["session_id"] = info["session_id"] or rec.get("sessionId")
        info["cwd"] = info["cwd"] or rec.get("cwd")
        info["branch"] = info["branch"] or rec.get("gitBranch")
        ts = rec.get("timestamp")
        if ts:
            info["start"] = info["start"] or ts
            info["end"] = ts
        if info["first_prompt"] is None and rec.get("type") == "user":
            text = " ".join(
                str(b.get("text", "")) for b in blocks_of(rec) if b.get("type") == "text"
            ).strip()
            # Skip tool-result-only user turns and system-injected noise.
            if text and not text.startswith("<"):
                info["first_prompt"] = text[:160].replace("\n", " ")
    return info


def cmd_search(args) -> int:
    root = Path(args.root) if args.root else default_root()
    if not root.exists():
        print(f"No transcript directory at {root}", file=sys.stderr)
        print("Point --root at your .claude/projects folder.", file=sys.stderr)
        return 1

    files = sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        print(f"No .jsonl transcripts under {root}", file=sys.stderr)
        return 1

    if args.regex:
        pats = [re.compile(p, re.IGNORECASE) for p in args.patterns]
        match = lambda text: sum(len(p.findall(text)) for p in pats)
    else:
        lowered = [p.lower() for p in args.patterns]
        match = lambda text: sum(text.lower().count(p) for p in lowered)

    print(f"Scanning {len(files)} transcript(s) under {root}\n")
    hits = 0
    for path in files:
        total = sum(match(record_text(rec)) for rec in iter_records(path))
        if not total:
            continue
        hits += 1
        info = summarise(path)
        mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {path}")
        print(f"    {total} match(es) · {info['records']} records · modified {mtime}")
        if info["session_id"]:
            print(f"    session {info['session_id']}")
        if info["cwd"]:
            print(f"    cwd     {info['cwd']}" + (f"  [{info['branch']}]" if info["branch"] else ""))
        if info["first_prompt"]:
            print(f"    opened  \"{info['first_prompt']}\"")
        print()

    if not hits:
        print("No matches. Try fewer or different terms, or a wider --root.")
        return 1
    print(f"{hits} transcript(s) matched. Extract one with:")
    print("  python3 recover_session.py extract <path> --out recovered/")
    return 0


def collect_files(rec: dict, out: dict) -> None:
    """Reconstruct file content from Write tool calls and shell heredocs."""
    for b in blocks_of(rec):
        if b.get("type") != "tool_use":
            continue
        name, inp = b.get("name"), b.get("input")
        if not isinstance(inp, dict):
            continue
        if name in WRITE_TOOLS:
            p = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
            c = inp.get("content")
            if p and isinstance(c, str):
                out[str(p)] = c
        elif name in EDIT_TOOLS:
            # Edits are deltas, not content; record that the file was touched.
            p = inp.get("file_path")
            if p:
                out.setdefault(str(p), None)
        elif name == "Bash":
            for m in HEREDOC.finditer(str(inp.get("command", ""))):
                out[m.group("path")] = m.group("body")


def cmd_extract(args) -> int:
    src = Path(args.transcript)
    if not src.exists():
        print(f"No such transcript: {src}", file=sys.stderr)
        return 1

    outdir = Path(args.out)
    (outdir / "files").mkdir(parents=True, exist_ok=True)

    info = summarise(src)
    lines: list[str] = [
        f"# Recovered session — {src.name}",
        "",
        f"- **Session:** `{info['session_id'] or 'unknown'}`",
        f"- **Working dir:** `{info['cwd'] or 'unknown'}`"
        + (f" (branch `{info['branch']}`)" if info["branch"] else ""),
        f"- **Span:** {info['start'] or '?'} → {info['end'] or '?'}",
        f"- **Records:** {info['records']}",
        "",
        "---",
        "",
    ]

    files: dict[str, str | None] = {}
    for rec in iter_records(src):
        rtype = rec.get("type")
        if rtype not in ("user", "assistant"):
            continue
        collect_files(rec, files)

        for b in blocks_of(rec):
            btype = b.get("type")
            if btype == "text":
                text = str(b.get("text", "")).strip()
                # Tool results and system reminders arrive as user "text"; skip them.
                if not text or (rtype == "user" and text.startswith("<")):
                    continue
                lines.append("## You" if rtype == "user" else "## Claude")
                lines.append("")
                lines.append(text)
                lines.append("")
            elif btype == "thinking" and args.include_thinking:
                lines.append("<details><summary>thinking</summary>\n")
                lines.append(str(b.get("thinking") or b.get("text") or "").strip())
                lines.append("\n</details>\n")
            elif btype == "tool_use" and args.include_tools:
                inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                hint = inp.get("file_path") or inp.get("query") or inp.get("url") or inp.get("command") or ""
                lines.append(f"`[{b.get('name')}]` {str(hint)[:120]}")
                lines.append("")

    transcript_md = outdir / "transcript.md"
    transcript_md.write_text("\n".join(lines), encoding="utf-8")

    written = 0
    for original, content in sorted(files.items()):
        if content is None:
            continue
        # Flatten the original path into a single safe filename.
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", original.lstrip("/\\")) or "unnamed"
        # Heredoc bodies stop before the closing tag's newline; restore it.
        if not content.endswith("\n"):
            content += "\n"
        (outdir / "files" / safe).write_text(content, encoding="utf-8")
        written += 1

    print(f"Wrote {transcript_md}")
    print(f"Recovered {written} file(s) into {outdir / 'files'}")
    edited_only = [p for p, c in files.items() if c is None]
    if edited_only:
        print("\nEdited but not fully reconstructable (deltas only, no full content in transcript):")
        for p in edited_only:
            print(f"  {p}")
    if written:
        print("\nRecovered file paths:")
        for original, content in sorted(files.items()):
            if content is not None:
                print(f"  {original}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Find and extract content from local Claude Code session transcripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = ap.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="find transcripts containing given terms")
    s.add_argument("patterns", nargs="+", help="terms to search for (any match counts)")
    s.add_argument("--root", help="transcript dir (default: ~/.claude/projects)")
    s.add_argument("--regex", action="store_true", help="treat patterns as regular expressions")
    s.set_defaults(func=cmd_search)

    e = sub.add_parser("extract", help="dump one transcript to markdown + recovered files")
    e.add_argument("transcript", help="path to a .jsonl transcript")
    e.add_argument("--out", default="recovered", help="output directory (default: recovered/)")
    e.add_argument("--include-thinking", action="store_true", help="keep reasoning blocks")
    e.add_argument("--include-tools", action="store_true", help="keep one-line tool call log")
    e.set_defaults(func=cmd_extract)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
