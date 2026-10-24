#!/usr/bin/env python3
"""원고 규약·사실·품질 체크리스트 기계적 검증기 (Mechanical Enforcement — 원칙 5).

검사 항목:
  E (Error — 승인/출판 차단):
    1. 최상단 HTML 메타데이터 주석(`<!-- chapter: ... -->`) 존재 여부
    2. YAML front-matter 필수 키 존재 + status 값 유효성
    3. 파일명 slug == front-matter slug, 그리고 `docs/toc.json`에 등록 여부
    4. front-matter `official_links` == `docs/toc.json`의 `official_links`
    5. 금지 표현(denylist) 미포함 (`docs/verified-facts.md` §4 동기화)
    6. 분량 게이트: `status >= draft`인 원고는 본문 단어(어절) 수 **2,500~4,000 단어** 필수
    7. 코드 블록 실행 가능성 게이트: Python 코드 블록(` ```python `)의 `ast.parse()` 문법 무결성 검증
    8. 강제 도장 게이트: `status`가 `reviewed`, `approved`, `published`인 경우
       `crosscheck: pass` 및 `humanized: pass` 필수 강제

사용:
    python scripts/verify.py            # errors 있으면 exit 1
    python scripts/verify.py --strict   # warnings도 exit 1
"""
from __future__ import annotations
import ast
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _harness import (chapter_path, count_words, iter_manuscript_files,
                      iter_toc_chapters, load_toc, parse_front_matter,
                      parse_metadata_comment)

REQUIRED_KEYS = [
    "part", "chapter", "slug", "title", "status",
    "official_links", "last_verified",
    "crosscheck", "crosscheck_date", "humanized", "humanized_date",
]
VALID_STATUS = {"skeleton", "draft", "revised", "proofread", "reviewed", "approved", "published"}
ACTIVE_STATUS = {"draft", "revised", "proofread", "reviewed", "approved", "published"}
GATED_STATUS = {"reviewed", "approved", "published"}

MIN_WORDS = 2500
MAX_WORDS = 4000

# docs/verified-facts.md §4의 denylist와 동기화
DENYLIST = [
    (r"OpenAI(이|가)?\s*(만든|발표한|정의한|공식)?\s*(5|8|12)\s*원칙",
     "출처 오류 — 원문은 원칙을 번호로 명시하지 않음. '원문에서 도출한 8원칙'으로 표기"),
    (r"한\s*절당\s*한\s*원칙으로\s*도출",
     "출처 오류 — 원문 11개 절 중 8개만 원칙으로 도출(1:1 전수 매핑 아님). '8개 절을 한 원칙씩 선별·도출'로 표기"),
    (r"12[\s-]*Factor\s*Agents?", "폐기된 구 주제 — '하네스 엔지니어링(Harness Engineering)'으로 표기"),
    (r"HumanLayer", "폐기된 구 출처 — OpenAI / Ryan Lopopolo로 표기"),
    (r"Dexter\s*Horthy", "폐기된 구 출처 — OpenAI / Ryan Lopopolo로 표기"),
    (r"docs\.claude\.com/docs", "구 도메인 — 'code.claude.com/docs'로 표기"),
    (r"정본", "용어 통일 규칙 위반 — 독자 대상 본문은 '원문'으로 표기"),
]


def verify_python_blocks(rel_path: str, body: str) -> list[str]:
    """본문 내 모든 ```python 코드 블록이 문법 오류 없이 파싱(ast.parse) 가능한지 검증."""
    errs = []
    blocks = re.findall(r"```python\s*\n(.*?)```", body, re.DOTALL)
    for idx, code in enumerate(blocks, 1):
        try:
            ast.parse(code)
        except SyntaxError as exc:
            errs.append(f"{rel_path}: Python 코드 블록 #{idx} 문법 오류 (실행 불가): {exc}")
    return errs


def main():
    strict = "--strict" in sys.argv
    toc = load_toc()
    by_slug = {ch["slug"]: (part, ch) for part, ch in iter_toc_chapters(toc)}

    errors, warnings = [], []

    for slug, (_, ch) in by_slug.items():
        if not os.path.exists(chapter_path(slug)):
            warnings.append(f"{slug}: toc.json에 등록되어 있으나 원고 파일 없음 (`python scripts/scaffold.py` 실행 권장)")

    for path, text in iter_manuscript_files():
        rel = os.path.relpath(path)
        meta_comment = parse_metadata_comment(text)
        if not meta_comment or "chapter" not in meta_comment or "status" not in meta_comment:
            errors.append(f"{rel}: 최상단 1행 HTML 메타데이터 주석(`<!-- chapter: ..., status: ... -->`) 누락")

        fm, body = parse_front_matter(text)
        if not fm:
            errors.append(f"{rel}: front-matter 없음")
            continue

        for k in REQUIRED_KEYS:
            if k not in fm:
                errors.append(f"{rel}: front-matter 필수 키 '{k}' 누락")

        status = fm.get("status")
        if status not in VALID_STATUS:
            errors.append(f"{rel}: status '{status}' 유효하지 않음 {sorted(VALID_STATUS)}")

        fname_slug = os.path.basename(path)[:-3]
        if fm.get("slug") != fname_slug:
            errors.append(f"{rel}: 파일명({fname_slug}) != front-matter slug({fm.get('slug')})")

        if fname_slug not in by_slug:
            warnings.append(f"{rel}: docs/toc.json에 등록되지 않은 slug")
        else:
            toc_links = by_slug[fname_slug][1].get("official_links", [])
            fm_links = fm.get("official_links") or []
            if sorted(toc_links) != sorted(fm_links):
                errors.append(
                    f"{rel}: official_links가 docs/toc.json과 불일치\n"
                    f"      toc: {toc_links}\n      fm : {fm_links}"
                )

        # 금지 표현(denylist) 검사
        for pat, hint in DENYLIST:
            for m in re.finditer(pat, body):
                errors.append(f"{rel}: 금지 표현 '{m.group(0)}' 검출 — {hint}")

        # draft 이상인 원고는 분량(2,500~4,000 단어) 및 코드 블록 실행 가능성 검사
        if status in ACTIVE_STATUS:
            words = count_words(body)
            if not (MIN_WORDS <= words <= MAX_WORDS):
                errors.append(
                    f"{rel}: 분량 기준(2,500~4,000 단어) 위반 (현재 {words} 단어)"
                )
            errors.extend(verify_python_blocks(rel, body))

        # reviewed/approved/published 상태는 crosscheck=pass 및 humanized=pass 도장 강제
        if status in GATED_STATUS:
            if fm.get("crosscheck") != "pass":
                errors.append(
                    f"{rel}: status '{status}'인데 crosscheck != pass (현재: {fm.get('crosscheck')}). "
                    f"`python scripts/crosscheck.py {fname_slug}` 통과 필요"
                )
            if fm.get("humanized") != "pass":
                errors.append(
                    f"{rel}: status '{status}'인데 humanized != pass (현재: {fm.get('humanized')}). "
                    f"proofreader AI 티 제거 윤문 통과 필요"
                )

    for w in warnings:
        print(f"[WARN]  {w}")
    for e in errors:
        print(f"[ERROR] {e}")
    print("\n" + "─" * 50)
    print(f"검증 결과: errors {len(errors)} · warnings {len(warnings)}")
    if errors or (strict and warnings):
        print("FAIL ❌")
        sys.exit(1)
    print("PASS ✅ (모든 기계적 불변식 및 품질 게이트 통과)")


if __name__ == "__main__":
    main()
