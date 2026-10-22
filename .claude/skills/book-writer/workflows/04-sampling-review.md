# Workflow 04: Sampling Review Mode (표본 추출 기반 신속 품질 진단)

> **Lazy Load Notice**: 이 문서는 대량 원고 중 일부를 추출해 빠르게 감사하는 **샘플링 리뷰(`sampling-review`)** 요청 시에만 로드됩니다.

## 1. 목적 및 설계 원칙 (Why-First)

10개 이상의 챕터를 매번 전수 조사하면 막대한 컨텍스트 예산과 비용이 소모됩니다. 각 챕터의 도입부, 가장 복잡한 코드 블록이 포함된 핵심 절, 결론부를 표본(Sample)으로 추출하여 읽기 전용 리뷰어들만 투입함으로써 최소 비용으로 전체 원고의 체계적 결함(Systematic Bias)을 조기 발견합니다.

## 2. 실행 절차 및 직접 소통 프로토콜

1. **표본 구간 선정 (`structure-reviewer` - Sonnet)**
   - 각 대상 챕터의 메타데이터 주석, 단어 수(2,500~4,000 단어 여부), 헤딩 구조를 빠르게 스캔하고 가장 밀도가 높은 핵심 섹션 위치를 선정하여 동료 리뷰어들에게 `SendMessage`로 공유합니다.
2. **병렬 샘플 감사 (`fact-checker` & `tech-reviewer`)**
   - `fact-checker`(Sonnet): 샘플 구간의 통계/인용구 진위 여부를 점검합니다.
   - `tech-reviewer`(Opus): 샘플 구간의 대표 코드 블록이 실행 가능한지, Why-First 원칙에 맞게 설명되었는지 진단합니다.
3. **종합 품질 스코어카드 발행 (`chapter-reviewer` - Opus)**
   - `fact-checker`, `tech-reviewer`, `structure-reviewer`로부터 `SendMessage`로 진단 결과를 취합하여 전체 원고의 건강도(Pass / Warn / Fail)와 우선 개고 대상 챕터를 사용자에게 보고합니다. (이 모드에서는 원고를 직접 수정하지 않습니다.)
