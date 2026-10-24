#!/usr/bin/env python3
"""docs/toc.json → manuscripts/*.md 골격 생성기 (결정론적 산출물 · 멱등성 보장).

Why-First 설계 이유:
에이전트가 원고 파일을 매번 수동으로 만들면 front-matter 필수 키나 최상단 메타데이터 주석,
공식 링크(official_links)가 누락되기 쉽다. 따라서 구조의 진실의 원천인 `docs/toc.json`에서
원고 골격을 결정론적으로 생성하되, 이미 작성 중인 파일은 절대 덮어쓰지 않도록(멱등성) 보호한다.

사용:
    python scripts/scaffold.py            # 누락된 챕터 골격만 생성
    python scripts/scaffold.py --dry-run  # 생성 대상만 미리보기
"""
from __future__ import annotations
import os
import sys

from _harness import MANUSCRIPT_DIR, chapter_path, iter_toc_chapters, load_toc

TEMPLATE = """<!-- chapter: {chapter_pad}, title: "{title}", word_count: 0, status: skeleton, author: chapter-writer, reviewers: [fact-checker, tech-reviewer, structure-reviewer, proofreader, chapter-reviewer] -->
---
part: {part}
chapter: {chapter}
slug: {slug}
title: "{title}"
status: skeleton
word_count: 0
wikidocs_page_id: null
parent_page_id: {parent_page_id}
official_links:
{links_yaml}
last_verified: null
crosscheck: null
crosscheck_date: null
humanized: null
humanized_date: null
---

# {chapter}장. {title}

## 이 장에서 배우는 것

<!-- 한 줄로: 이 장을 끝내면 독자가 무엇을 할 수 있나 -->

## 핵심 개념

<!-- 핵심 패턴/원칙 한 줄 정의 + 비유 + 원문 인용 (Why-First) -->

## 왜 중요한가

<!-- 이 원칙을 어기면 무엇이 무너지는가 (단일 거대 에이전트 vs 오케스트레이션 하네스) -->

## 하네스에 적용하기

<!-- 실제 실행 가능한 코드 블록 + 7인 에이전트 프로토콜/디렉터리 구조 -->

## 안티패턴과 함정

<!-- 흔한 잘못된 적용(우체국 안티패턴, 권한 과잉, 사실 복제 등)과 해결책 -->

## 핵심 정리 / 체크리스트

- [ ] 메타데이터 주석 및 front-matter 포함 확인
- [ ] 본문 분량 2,500~4,000 단어 충족 확인
- [ ] 코드 블록 실행 가능성 및 Why-First 설명 확인

## 공식 출처

{links_md}
"""


def links_block(links: list[str]) -> tuple[str, str]:
    if not links:
        return "  []", "<!-- docs/toc.json의 official_links만 사용 -->"
    yaml_str = "\n".join(f"  - {u}" for u in links)
    md_str = "\n".join(f"- {u}" for u in links)
    return yaml_str, md_str


def main():
    dry = "--dry-run" in sys.argv
    os.makedirs(MANUSCRIPT_DIR, exist_ok=True)
    toc = load_toc()
    created, skipped = 0, 0
    for part, ch in iter_toc_chapters(toc):
        path = chapter_path(ch["slug"])
        if os.path.exists(path):
            skipped += 1
            continue
        part_label = "부록" if part.get("is_appendix") else part["part"]
        ch_num = ch["chapter"]
        ch_pad = f"{ch_num:02d}" if isinstance(ch_num, int) else str(ch_num)
        links_yaml, links_md = links_block(ch.get("official_links", []))
        content = TEMPLATE.format(
            chapter_pad=ch_pad,
            part=part_label,
            chapter=ch_num,
            slug=ch["slug"],
            title=ch["title"].replace('"', "'"),
            parent_page_id=part.get("wikidocs_page_id", "null"),
            links_yaml=links_yaml,
            links_md=links_md,
        )
        if dry:
            print(f"[would create] {os.path.relpath(path)}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[created] {os.path.relpath(path)}")
        created += 1
    print(f"\n생성 {created} · 기존유지 {skipped}" + (" (dry-run)" if dry else ""))


if __name__ == "__main__":
    main()
