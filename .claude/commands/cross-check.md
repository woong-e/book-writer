---
description: 진실의 원천(docs/verified-facts.md) 및 독립 검증기로 한 장의 기술 사실을 교차 검증하고 crosscheck 도장을 찍는다.
argument-hint: <slug 또는 --facts> (예: chapter-01)
---

`$ARGUMENTS` 장을 `fact-checker` 및 `scripts/crosscheck.py`로 교차 검증한다:

```bash
python scripts/crosscheck.py $ARGUMENTS
```

- 원고의 8원칙 명칭·순서, 7인 에이전트 권한 매트릭스, Why-First 코드 스펙(`pdfplumber` vs `PyPDF2` 등)이 `docs/verified-facts.md`와 일치하는지 검사한다.
- 결과 JSON은 `.harness-cache/crosscheck/<slug>.json`에 보존되며, 차단급 오류가 없으면 원고 front-matter에 `crosscheck: "pass"` 도장을 자동으로 찍는다.
