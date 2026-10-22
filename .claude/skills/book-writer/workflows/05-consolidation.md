# Workflow 05: Consolidation Mode (다중 챕터 서사·용어·맥락 정합성 통합)

> **Lazy Load Notice**: 이 문서는 여러 챕터 간의 중복 제거 및 맥락 통일을 위한 **`consolidation`** 모드 요청 시에만 로드됩니다.

## 1. 목적 및 설계 원칙 (Why-First)

여러 챕터를 병렬로 집필하다 보면 2장에서 설명한 기초 개념을 4장에서 또다시 장황하게 설명하거나, 앞장에서 설정한 도메인 배경(사회 구조, 시스템 갈등 구조, 예제 프로젝트 시나리오)이 뒷장에서 미묘하게 달라지는 현상이 발생합니다. `consolidation` 모드는 챕터 간 경계를 넘어 단행본 전체의 유기적 일관성을 확보합니다.

## 2. 실행 절차 및 직접 소통 프로토콜

1. **도메인 맥락 및 리서치 정합성 대조 (`researcher` & `structure-reviewer`)**
   - `researcher`(Opus)는 각 챕터에 적용된 도메인 설정, 사회/갈등 구조 또는 아키텍처 진화 시나리오가 일관된지 확인합니다.
   - `structure-reviewer`(Sonnet)는 챕터 간 중복 설명 구간과 분량 편차를 찾아내어 `SendMessage`로 `chapter-writer`에게 알립니다.
2. **용어 및 문체 단일화 (`proofreader` - Sonnet)**
   - `Grep`으로 전체 원고에서 `references/glossary.md`에 위배되는 이표기(예: 에이전트/대리자, 하네스/프레임워크 혼용)를 색출하여 `SendMessage`로 `chapter-writer`에게 통일안을 전달합니다.
3. **챕터 간 브릿지 문단 수정 (`chapter-writer` - Opus)**
   - 중복된 설명은 앞 챕터 참조로 압축하고, 각 챕터의 시작과 끝에 이전 챕터의 결론과 다음 챕터의 문제의식을 잇는 브릿지(Bridge) 문단을 보강합니다. 수정 후에도 각 챕터가 2,500~4,000 단어 기준을 유지하는지 확인합니다.
