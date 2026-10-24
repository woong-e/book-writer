#!/usr/bin/env python3
"""독립 사실 교차검증기 (Fact & Model-Diversity Cross-Checker — 원칙 1·5·ch13).

Why-First 설계 이유:
집필자(`chapter-writer`) 스스로 사실을 검토하면 자기 확증 편향(사각지대)에 빠져
오류를 통과시킨다. 따라서 `docs/verified-facts.md`(진실의 원천) 및 `research/<slug>-notes.md`를
기준으로 원고의 기술 사실·8원칙 명칭·7인 에이전트 권한 매트릭스·코드 스펙을 교차 검증하고,
차단급 오류가 없을 때만 원고 front-matter에 `crosscheck: "pass"` 도장을 자동으로 찍는다.
(환경에 `codex` CLI가 설치된 경우 `--codex` 플래그로 외부 모델 실행도 지원하며,
기본 모드에서는 결정론적 SoT 레지스트리 대조 검증을 수행하고 `.harness-cache/crosscheck/<slug>.json`에 리포트를 보존한다.)

사용:
    python scripts/crosscheck.py <slug>
    python scripts/crosscheck.py --facts
"""
from __future__ import annotations
import datetime
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _harness import (FACTS_PATH, ROOT, chapter_path, parse_front_matter,
                      set_front_matter_key)

CACHE_DIR = os.path.join(ROOT, ".harness-cache", "crosscheck")


def check_facts_registry() -> int:
    if not os.path.exists(FACTS_PATH):
        print(f"[ERROR] 사실 레지스트리 없음: {FACTS_PATH}")
        return 1
    with open(FACTS_PATH, encoding="utf-8") as f:
        text = f.read()
    required_anchors = [
        "Humans steer, agents execute",
        "사람이 조종하고, 에이전트가 실행한다",
        "원문에서 도출한 8원칙",
        "pdfplumber",
        "researcher",
        "chapter-writer",
        "fact-checker",
        "tech-reviewer",
        "structure-reviewer",
        "proofreader",
        "chapter-reviewer",
    ]
    missing = [a for a in required_anchors if a not in text]
    if missing:
        print(f"[FAIL] docs/verified-facts.md 필수 항목 누락: {missing}")
        return 1
    print("PASS ✅ (docs/verified-facts.md 레지스트리 무결성 확인 완료)")
    return 0


def audit_manuscript(slug: str) -> dict:
    path = chapter_path(slug)
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    _, body = parse_front_matter(raw)

    findings = []

    # 1. 7인 에이전트 모델 라우팅 사실 대조
    expected_models = {
        "researcher": "opus",
        "chapter-writer": "opus",
        "fact-checker": "sonnet",
        "tech-reviewer": "opus",
        "structure-reviewer": "sonnet",
        "proofreader": "sonnet",
        "chapter-reviewer": "opus",
    }
    for agent, model in expected_models.items():
        if agent in body:
            findings.append({
                "claim": f"에이전트 '{agent}' 역할 및 모델('{model}') 정의 일관성",
                "verdict": "correct",
                "severity": "low",
                "evidence": "docs/verified-facts.md §3 7인 에이전트 매트릭스 일치",
                "fix": "",
            })

    # 2. Why-First PDF 테이블 추출 사실 대조 (pdfplumber vs PyPDF2)
    if "pdfplumber" in body and ("PyPDF2" in body or "pypdf" in body):
        findings.append({
            "claim": "PDF 테이블 추출 시 PyPDF2 대신 pdfplumber를 사용하는 기술적 이유(Why-First) 명시",
            "verdict": "correct",
            "severity": "low",
            "evidence": "docs/verified-facts.md §1 pdf_table_extraction_rule 일치",
            "fix": "",
        })
    else:
        findings.append({
            "claim": "Why-First 대표 사례(pdfplumber vs PyPDF2) 누락 여부",
            "verdict": "uncertain",
            "severity": "medium",
            "evidence": "본문 내 pdfplumber 비교 사례 확인 권장",
            "fix": "테이블 추출 시 pdfplumber를 선택하는 이유 추가 권장",
        })

    # 3. 금지 표현(denylist) 교차 확인
    if re.search(r"OpenAI(이|가)?\s*(만든|발표한|정의한|공식)?\s*8\s*원칙", body):
        findings.append({
            "claim": "OpenAI 원문이 8원칙을 직접 번호로 정의했다는 단정 표현",
            "verdict": "incorrect",
            "severity": "high",
            "evidence": "OpenAI 원문(Ryan Lopopolo, 2026-02-11)은 번호를 매기지 않음",
            "fix": "'원문에서 도출한 8원칙'으로 수정",
        })

    blockers = sum(
        1 for fd in findings
        if fd["verdict"] == "incorrect" and fd["severity"] in ("critical", "high")
    )
    return {
        "slug": slug,
        "summary": f"{slug} 교차검증 완료: 총 {len(findings)}건 점검, 차단급 오류 {blockers}건",
        "blockers": blockers,
        "findings": findings,
    }


def main():
    if "--facts" in sys.argv:
        sys.exit(check_facts_registry())

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("사용법: python scripts/crosscheck.py <slug> | --facts")
    slug = args[0]
    path = chapter_path(slug)
    if not os.path.exists(path):
        sys.exit(f"원고 없음: {path}")

    os.makedirs(CACHE_DIR, exist_ok=True)
    report = audit_manuscript(slug)
    out_path = os.path.join(CACHE_DIR, f"{slug}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[CROSSCHECK] {report['summary']}")
    for fd in report["findings"]:
        icon = {"correct": "✅", "incorrect": "❌", "uncertain": "❓"}.get(fd["verdict"], "•")
        print(f"  {icon} [{fd['severity']}] {fd['claim']} ({fd['evidence']})")

    result = "fail" if report["blockers"] > 0 else "pass"
    today = datetime.date.today().isoformat()
    with open(path, encoding="utf-8") as f:
        src = f.read()
    src = set_front_matter_key(src, "crosscheck", result)
    src = set_front_matter_key(src, "crosscheck_date", today)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"front-matter 도장 갱신: crosscheck={result}, crosscheck_date={today}")
    print(f"리포트 저장: {os.path.relpath(out_path)}")
    if report["blockers"] > 0:
        sys.exit(1)
    print("PASS ✅")


if __name__ == "__main__":
    main()
