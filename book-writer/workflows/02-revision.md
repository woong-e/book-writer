# Workflow 02: Revision Mode (기존 원고 개고 및 재검증 파이프라인)

> **Lazy Load Notice**: 이 문서는 기존에 작성된 챕터 원고의 **수정/개고(`revision`)** 요청 시에만 조건부로 로드됩니다.

## 1. 목적 및 컨텍스트 절약 설계 (Why-First)

전체 챕터를 처음부터 다시 쓰는 대신 문제가 지적된 섹션이나 변경된 기술 사양만 타깃팅하여 수정합니다. 이미 검증된 리서치 노트가 존재하므로 `researcher`는 기본적으로 대기 상태로 두고, 새로운 외부 팩트가 추가될 때만 온디맨드로 호출하여 토큰 비용을 절감합니다.

## 2. 실행 절차 및 직접 소통 프로토콜

1. **변경 범위 분석 (`chapter-writer` - Opus)**
   - 대상 원고(`manuscripts/chapter-XX.md`)의 상단 메타데이터 주석과 수정 요청 사항을 읽습니다.
   - 코드 및 아키텍처 변경이 포함된 경우 `tech-reviewer`에게, 팩트 보강이 필요한 경우 `fact-checker`에게 `SendMessage`로 사전 검토 의견을 구합니다.
2. **원고 수정 및 자기 점검 (`chapter-writer`)**
   - `Edit` 도구로 해당 절을 수정하고, 수정 후에도 전체 분량이 **2,500~4,000 단어** 범위를 유지하는지, 코드 블록이 실행 가능한지 자체 점검합니다.
3. **타깃 검증 (`fact-checker` / `tech-reviewer` -> `proofreader`)**
   - 수정된 단락에 대해서만 `fact-checker`(Sonnet)와 `tech-reviewer`(Opus)가 읽기 전용으로 검증하고 `SendMessage`로 피드백을 회신합니다.
   - 반영 완료 후 `proofreader`(Sonnet)가 새로 작성된 문장의 어조가 기존 문단과 자연스럽게 이어지는지 윤문 제안을 보냅니다.
4. **최종 승인 (`chapter-reviewer` - Opus)**
   - 수정 부위가 챕터 전체의 서사 흐름을 깨뜨리지 않았는지 확인 후 메타데이터 상태를 `status: approved`로 갱신 승인합니다.
