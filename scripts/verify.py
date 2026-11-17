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
    (r"1\s*:\s*(10|20|30)\s*:\s*300",
     "통계 수치 오류 — 하인리히 법칙의 정확한 비율은 '1:29:300'임"),
    (r"개인보호구\(PPE\)를\s*최우선\s*대책으로",
     "위험 통제 계층(Hierarchy of Controls) 위반 — 제거·대체·공학적 대책이 우선이며 PPE는 최후의 방어선임"),
    (r"산업안전보건법\s*제4조에\s*따른\s*위험성평가",
     "법 조항 착오 — 위험성평가는 '산업안전보건법 제36조'이며, 안전보건확보의무가 '중대재해처벌법 제4조'임"),
    (r"docs\.claude\.com/docs", "구 도메인 — 'code.claude.com/docs'로 표기"),
    (r"정본", "용어 통일 규칙 위반 — 독자 대상 본문은 '원문' 또는 '공식 지침'으로 표기"),
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


def verify_skill_antipatterns() -> tuple[list[str], list[str]]:
    """ex-05-12-antipatterns의 3대 스킬 안티패턴(거대 본문 / references 부재 / 이유 없는 규칙)을 기계적으로 감사."""
    errs, warns = [], []
    skill_dir = os.path.join(".claude", "skills", "book-writer")
    skill_md = os.path.join(skill_dir, "SKILL.md")
    refs_dir = os.path.join(skill_dir, "references")
    workflows_dir = os.path.join(skill_dir, "workflows")

    if not os.path.isfile(skill_md):
        errs.append(f"{skill_md}: 스킬 정의 파일이 존재하지 않음")
        return errs, warns

    with open(skill_md, encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    line_count = len(lines)

    # 1. 안티패턴 1 (거대 본문): wc -l >= 500 발현 차단 (권고 상한 150행 모니터링)
    if line_count >= 500:
        errs.append(
            f"{skill_md}: 안티패턴 1(거대 본문) 발현 — 현재 {line_count}행 (임계치 500행 이상). "
            f"Progressive Disclosure 원칙에 따라 세부 절차를 workflows/로 분리 필요"
        )
    elif line_count > 150:
        warns.append(
            f"{skill_md}: 본문 라인 수({line_count}행)가 권고 기준(150행)을 초과함 — workflows/ 외부화 권장"
        )

    # 2. 안티패턴 2 (references 부재): references/ 디렉토리 및 Layer 3 프리셋 존재 확인
    if not os.path.isdir(refs_dir) or not os.listdir(refs_dir):
        errs.append(
            f"{skill_md}: 안티패턴 2(references 부재) 발현 — {refs_dir} 디렉토리가 없거나 비어 있음 (Layer 3 분리 위반)"
        )

    # 3. 안티패턴 3 (이유 없는 규칙): 강제 키워드 >= 5 AND 인과 키워드 == 0 차단
    coercive_cnt = len(re.findall(r"ALWAYS|NEVER|반드시|절대", content))
    causal_cnt = len(re.findall(r"왜냐하면|때문에", content))
    if coercive_cnt >= 5 and causal_cnt == 0:
        errs.append(
            f"{skill_md}: 안티패턴 3(이유 없는 규칙 / Why-First 위반) 발현 — "
            f"강제 키워드 {coercive_cnt}건 대비 인과 근거('왜냐하면|때문에') 0건"
        )

    # 워크플로 파일들의 Why-First 인과 근거(왜냐하면|때문에) 유무 점검
    if os.path.isdir(workflows_dir):
        for wf_name in sorted(os.listdir(workflows_dir)):
            if not wf_name.endswith(".md"):
                continue
            wf_path = os.path.join(workflows_dir, wf_name)
            with open(wf_path, encoding="utf-8") as wf:
                wf_text = wf.read()
            if not re.search(r"왜냐하면|때문에|Why-First", wf_text):
                warns.append(f"{wf_path}: Why-First 인과 해설('왜냐하면|때문에') 보강 권장")

    return errs, warns


def main():
    strict = "--strict" in sys.argv
    toc = load_toc()
    by_slug = {ch["slug"]: (part, ch) for part, ch in iter_toc_chapters(toc)}

    errors, warnings = [], []
    ap_errs, ap_warns = verify_skill_antipatterns()
    errors.extend(ap_errs)
    warnings.extend(ap_warns)

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
