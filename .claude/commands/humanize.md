---
description: 원고의 내용·사실·코드는 한 글자도 바꾸지 않고 번역투·이중 피동 등 10대 AI 티만 제거하여 자연스러운 한국어로 윤문한다.
argument-hint: <slug> (예: chapter-01)
---

`proofreader` 에이전트와 `.claude/skills/book-writer/references/ai-tell-taxonomy.md`, `references/glossary.md`를 사용하여 `manuscripts/$ARGUMENTS.md`의 문체를 윤문한다:

1. **의미 불변(Fidelity)**: 수치, 고유명사, 코드 블록, 메타데이터 주석, `docs/verified-facts.md`의 8원칙 표준 명칭은 절대 변경하지 않는다.
2. **10대 AI 티 제거**: 번역투(`~에 대해`, `~를 통해` 남발), 이중 피동(`~되어진다`), 기계적 병렬, 상투적 관용구(`결론적으로`, `시사하는 바가 크다`)를 능동형 한국어로 교정한다.
3. 교정 반영 후 front-matter에 `humanized: "pass"` 및 `humanized_date`를 기록하고, `python scripts/verify.py`를 다시 실행하여 사실·분량(2,500~4,000 단어)·코드 무결성이 그대로 유지되었는지 확인한다.
