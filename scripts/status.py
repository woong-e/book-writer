#!/usr/bin/env python3
"""집필 진행 상태 관측 스크립트 (Observability — 원칙 3·4).

Why-First 설계 이유:
진행 상태를 사람의 기억이나 외부 채팅 로그에 두면 세션이 끊길 때 유실된다.
따라서 각 원고(`manuscripts/<slug>.md`)의 front-matter 및 메타데이터 주석을
`docs/toc.json` 순서대로 스캔하여 현재 진척률과 검증 게이트 상태를 즉시 복원한다.

사용:
    python scripts/status.py
"""
from __future__ import annotations
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _harness import (chapter_path, count_words, iter_toc_chapters, load_toc,
                      parse_front_matter)

ICON = {
    "skeleton": "·",
    "draft": "✎",
    "revised": "↻",
    "proofread": "✦",
    "reviewed": "✓",
    "approved": "✔",
    "published": "★",
    "missing": "✗",
}
ORDER = ["skeleton", "draft", "revised", "proofread", "reviewed", "approved", "published"]


def main():
    toc = load_toc()
    counts = {k: 0 for k in ORDER}
    missing = 0
    rows = []
    cur_part = None
    for part, ch in iter_toc_chapters(toc):
        label = "부록" if part.get("is_appendix") else f"{part['part']}부"
        if label != cur_part:
            rows.append(("PART", f"{label}. {part['title']}"))
            cur_part = label
        path = chapter_path(ch["slug"])
        if not os.path.exists(path):
            rows.append(("CH", f"  {ICON['missing']} [{ch['chapter']}] {ch['title']} ({ch['slug']})  (파일 없음)"))
            missing += 1
            continue
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        fm, body = parse_front_matter(raw)
        st = fm.get("status", "skeleton")
        if st in counts:
            counts[st] += 1
        words = count_words(body)
        cc = fm.get("crosscheck") or "-"
        hm = fm.get("humanized") or "-"
        rows.append((
            "CH",
            f"  {ICON.get(st, '?')} [{ch['chapter']}] {ch['title']} ({ch['slug']})  "
            f"<{st}>  words={words}  crosscheck={cc}  humanized={hm}"
        ))

    print(f"\n[BOOK] {toc['book']['subject']}  (book_id={toc['book'].get('wikidocs_book_id')})")
    for kind, line in rows:
        print(line if kind == "CH" else f"\n■ {line}")

    total = sum(counts.values()) + missing
    print("\n" + "─" * 72)
    summary = "  ".join(f"{ICON[k]} {k}:{counts[k]}" for k in ORDER if counts[k] > 0)
    print(f"합계 {total}장  |  {summary}  |  ✗ missing:{missing}")
    done = counts["reviewed"] + counts["approved"] + counts["published"]
    if total:
        print(f"검증·승인 완료 진척률: {done}/{total} ({done * 100 // total}%)")


if __name__ == "__main__":
    main()
