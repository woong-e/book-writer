---
description: 책 집필·출판 진행 상태(`status.py`)와 원고 기계적 검증 결과(`verify.py`)를 한눈에 확인한다.
---

다음 두 스크립트를 실행하여 현재 집필 진행 상태와 품질 게이트 통과 여부를 보고한다:

```bash
python scripts/status.py     # 장별 status / 단어 수 / crosscheck·humanized 도장 / 진척률
python scripts/verify.py     # 메타데이터 주석·front-matter·denylist·분량(2,500~4,000단어)·코드 문법 검증
```

결과를 요약하고, 다음에 작업해야 할 장(`skeleton` 또는 `draft`)을 제안한다.
