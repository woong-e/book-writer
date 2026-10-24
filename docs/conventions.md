# 집필 규약 (Conventions)

> 새 장을 쓰거나 검토하기 전 이 문서를 따른다. 규약 위반은 `scripts/verify.py`가 기계적으로 검출한다(원칙 5).

---

## 1. 대상 독자와 Why-First 서술 원칙

- **독자**: 코딩 에이전트(Claude Code, Codex 등)와 다중 에이전트 하네스를 설계하는 개발자·아키텍트.
- **Why-First 원칙**: LLM 지시서와 본문 서술 모두 *"절대 X를 쓰지 마라"* 같은 강압적 금지 대신, **"왜(Why) 그 규칙이나 도구가 필요한가"**를 먼저 제시해 오버피팅을 방지한다.
  - 예: *"PDF에서 테이블을 추출할 때는 `pdfplumber`를 사용합니다. `PyPDF2`는 단순 텍스트 추출에 특화되어 표의 셀 경계와 레이아웃 구조를 보존하지 못하기 때문입니다."*

## 2. 원고 메타데이터 주석 및 Front-Matter 규격 (필수 — 원칙 3)

모든 원고(`manuscripts/<slug>.md`)는 **최상단 1행에 HTML 메타데이터 주석**을 포함하고, 이어서 **YAML front-matter**를 둔다. 진행 상태는 머릿속이나 외부 메모가 아니라 원고 내부에만 기록한다.

```markdown
<!-- chapter: 01, title: "다중 에이전트 오케스트레이션 하네스와 최소 권한 설계", word_count: 3450, status: approved, author: chapter-writer, reviewers: [fact-checker, tech-reviewer, structure-reviewer, proofreader, chapter-reviewer] -->
---
part: 1
chapter: 1
slug: chapter-01
title: "다중 에이전트 오케스트레이션 하네스와 최소 권한 설계"
status: "approved"
word_count: 3450
wikidocs_page_id: 363235
parent_page_id: 363213
official_links:
  - https://openai.com/index/harness-engineering/
  - https://code.claude.com/docs/en/sub-agents
  - https://modelcontextprotocol.io
last_verified: "2026-10-24"
crosscheck: "pass"
crosscheck_date: "2026-10-24"
humanized: "pass"
humanized_date: "2026-10-24"
---
```

## 3. 제출 전 4대 품질 게이트 (`scripts/verify.py` 강제)

1. **메타데이터 주석 및 Front-Matter 무결성**: 필수 키 누락 없음, `toc.json`의 `slug` 및 `official_links`와 일치.
2. **분량 예산 (2,500~4,000 단어)**: 본문 단어(어절) 수가 **2,500~4,000 단어** 범위 안에 있어야 한다.
3. **코드 블록 실행 가능성**: 모든 코드 블록에 언어 태그가 명시되고 생략(`...`) 없이 문법적으로 실행 가능해야 한다.
4. **교차검증(`crosscheck: pass`) 및 한국어 윤문(`humanized: pass`) 도장**:
   - `fact-checker` + `scripts/crosscheck.py` 통과 시 `crosscheck: pass` 자동 기록
   - `proofreader`의 AI 티 제거(번역투·이중 피동·관용구 교정) 통과 시 `humanized: pass` 기록
   - 둘 중 하나라도 `pass`가 아니면 `reviewed`/`approved`/`published` 상태로 승격할 수 없다.

## 4. 표준 6대 섹션 권장 구조

각 챕터는 독자의 인지 부하를 줄이기 위해 아래 논리 흐름(또는 이에 준하는 Why-First 절 구조)을 포함한다:
- `## 이 장에서 배우는 것` (학습 목표 요약)
- `## 핵심 개념` (한 줄 정의 + 비유 + 원문/아키텍처 근거)
- `## 왜 중요한가` (단일 거대 에이전트·하네스 부재 시 무너지는 지점)
- `## 하네스에 적용하기` (실제 코드·디렉터리 구조·7인 에이전트 프로토콜)
- `## 안티패턴과 함정` (우체국 안티패턴, 권한 과잉, 사실 복제 등)
- `## 핵심 정리 / 체크리스트` (제출 전 자기 점검 체크리스트)
- `## 공식 출처` (`toc.json`에 등록된 `official_links`)
