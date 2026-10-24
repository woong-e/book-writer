---
description: 7인 다중 에이전트 파이프라인(book-writer writing 모드)을 가동하여 한 장을 규약대로 집필·검증·교정·승인한다.
argument-hint: <slug> (예: chapter-01 또는 chapter-02)
---

`$ARGUMENTS` 장을 `book-writer` 스킬의 `writing` 모드([`workflows/01-writing.md`](../skills/book-writer/workflows/01-writing.md))에 따라 집필한다:

1. `docs/conventions.md`, `docs/verified-facts.md`, `docs/toc.json`을 확인한다.
2. 원고 파일(`manuscripts/$ARGUMENTS.md`)이 없으면 `python scripts/scaffold.py`로 골격을 먼저 생성한다.
3. **7인 다중 에이전트 파이프라인**을 가동한다:
   - `researcher` (Opus / Write) ➔ `research/$ARGUMENTS-notes.md` 작성 후 `SendMessage`로 `chapter-writer`에게 직접 브리핑
   - `chapter-writer` (Opus / Write) ➔ `manuscripts/$ARGUMENTS.md` 초고 작성 (상단 메타데이터 주석 + YAML front-matter + 2,500~4,000 단어 + 실행 가능 코드 블록 + Why-First 설명)
   - `[fact-checker (Sonnet) | tech-reviewer (Opus) | structure-reviewer (Sonnet)]` 3인 읽기 전용 병렬 검증 후 `SendMessage` 피드백 전달
   - `proofreader` (Sonnet / Read-Only) ➔ 한국어 AI 티 제거(`references/ai-tell-taxonomy.md`) 및 용어 통일(`references/glossary.md`) 후 `humanized: "pass"` 도장 부여
   - `chapter-reviewer` (Opus / Read-Only) ➔ 총괄 비평 및 `APPROVED` 판정
4. `python scripts/crosscheck.py $ARGUMENTS` 및 `python scripts/verify.py`를 실행하여 모든 기계적 게이트를 통과시킨다.
