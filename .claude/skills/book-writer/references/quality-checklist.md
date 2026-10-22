# 원고 품질 검증 체크리스트 (Quality Verification Checklist)

모든 작성(`chapter-writer`, `researcher`) 및 검토(`fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`) 에이전트는 후속 단계로 작업을 인계하기 전 아래 필수 요건을 검증해야 합니다.

## 1. 필수 3대 게이트 (Mandatory Quality Gates)

### ① 메타데이터 주석 포함 (Metadata Header Comment)
모든 챕터 원고(`manuscripts/chapter-XX.md`)의 최상단(1행)에는 아래와 같은 형식의 HTML 주석 메타데이터가 반드시 포함되어야 합니다.
```markdown
<!--
chapter: 01
title: "다중 에이전트 오케스트레이션 설계"
word_count: 3120
status: draft | revised | proofread | approved
author: chapter-writer
reviewers: [fact-checker, tech-reviewer, structure-reviewer, proofreader, chapter-reviewer]
-->
```
- **이유(Why)**: `compile` 및 `sampling-review` 모드에서 본문 전체를 컨텍스트에 로드하지 않고도 상단 몇 줄만 읽어 챕터의 승인 상태와 분량 규격 준수 여부를 즉시 파싱하기 위함입니다.

### ② 분량 기준: 2,500~4,000 단어 (Word Count Budget)
- 각 챕터의 본문 분량은 **최소 2,500 단어 이상, 최대 4,000 단어 이하**여야 합니다.
- **이유(Why)**: 2,500 단어 미만이면 배경 설명(Why)이나 실전 예제가 생략된 피상적인 요약글이 되기 쉽고, 4,000 단어를 초과하면 단일 챕터의 인지 부하가 과도해질 뿐 아니라 다중 에이전트가 동시에 검토할 때 컨텍스트 윈도우 예산을 초과 소비하기 때문입니다.

### ③ 코드 블록 실행 가능 (Executable Code Blocks)
- 본문에 포함된 모든 코드 블록은 문법 오류, 미선언 변수, 생략 기호(`// ... 생략 ...`)로 인한 실행 불능 상태가 없어야 합니다.
- **이유(Why)**: 독자가 책을 보며 실습할 때 가장 큰 좌절감을 느끼는 지점이 '복사해서 실행했는데 돌아가지 않는 예제 코드'이기 때문이며, 완결된 코드만이 `tech-reviewer`의 정적 분석을 통과할 수 있습니다.

---

## 2. 역할별 인계 전 점검 요약표

| 점검 주체 | 핵심 검증 항목 | 통과 기준 |
| :--- | :--- | :--- |
| **`researcher`** | 1차 출처 확보율, 버전 명시, 갈등/트레이드오프 구조화 | 공식 문서/논문 링크 포함 및 `SendMessage` 브리핑 완료 |
| **`chapter-writer`** | 메타데이터 주석, 2,500~4,000 단어, 코드 실행 가능, Why-First 서술 | 4개 항목 100% 자체 체크 후 3인 리뷰어에게 동시 발송 |
| **`fact-checker`** | 통계/인용/역사적 사실 대조, 환각 여부 | 오류 행 번호(Line)와 1차 출처 근거 함께 제시 |
| **`tech-reviewer`** | 코드 실행 가능성, 보안/성능 안티패턴, 텍스트-코드 정합성 | 대안 코드 스니펫과 기술적 이유(Why) 제시 |
| **`structure-reviewer`** | 헤딩 계층(H1~H3), 분량 밸런스(2,500~4,000 단어), 선행 지식 역전 | 절 간 호흡 및 단락 재배치 가이드 제시 |
| **`proofreader`** | 번역투/피동형 제거, `glossary.md` 용어 통일, 맞춤법 | 기술적 의미 왜곡 없는 문장 교정표 제시 |
| **`chapter-reviewer`** | 타깃 독자 몰입도, 차별화된 통찰, 3대 품질 게이트 최종 감사 | `APPROVED` 또는 구체적 사유가 담긴 `REVISION_REQUIRED` 판정 |
