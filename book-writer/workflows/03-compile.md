# Workflow 03: Compile Mode (단행본 원고 통합 및 출판 빌드 파이프라인)

> **Lazy Load Notice**: 이 문서는 개별 챕터를 하나로 묶는 **원고 통합(`compile`)** 요청 시에만 조건부로 로드됩니다.

## 1. 목적 및 설계 원칙 (Why-First)

개별 챕터가 아무리 훌륭해도 하나로 합쳤을 때 목차 번호가 어긋나거나 상호 참조("3장에서 다룬...")가 깨지면 단행본으로서의 완성도가 무너집니다. `compile` 모드는 본문 창작을 멈추고 구조적 무결성과 패키징에만 집중합니다.

## 2. 실행 절차 및 직접 소통 프로토콜

1. **챕터 메타데이터 전수 스캔 (`structure-reviewer` - Sonnet)**
   - `manuscripts/` 내 모든 챕터의 상단 HTML 주석(`<!-- chapter: XX, word_count: NNNN, status: approved -->`)을 스캔합니다.
   - 각 챕터가 2,500~4,000 단어 기준을 충족하는지, 미승인(`draft`) 상태인 챕터가 없는지 확인하여 `chapter-writer`에게 `SendMessage`로 전달합니다.
2. **상호 참조 및 용어 최종 감사 (`proofreader` - Sonnet)**
   - `Grep`을 사용하여 챕터 간 참조 문구와 `references/glossary.md` 표기 불일치를 검출하고 `SendMessage`로 수정 위치를 전달합니다.
3. **단행본 병합 및 목차 생성 (`chapter-writer` - Opus)**
   - 전체 목차(TOC), 서문, 챕터 본문, 부록을 순서대로 병합하여 `dist/book-compiled.md`를 생성하고 빌드 요약을 오케스트레이터에게 보고합니다.
