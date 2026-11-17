# 장르별·도메인별 스타일 프리셋 (Genre & Domain Style Presets — Layer 3 Extension)

> **아키텍처 매핑 (`cross-ref`)**: `antipattern-detector` **안티패턴 2 (`references` 부재 / Layer 3 분리)** 해결 권고에 따라, 단행본 도메인 확장 시 메인 `SKILL.md`를 비대화시키지 않고 동적으로 매핑할 수 있도록 분리한 Layer 3 프리셋입니다.

## 1. 프리셋 매핑 테이블

| 프리셋 ID (`preset`) | 대상 도메인 및 장르 | 핵심 서술 어조 (Tone & Manner) | 우선 참조 레지스트리 및 검증 규칙 |
| :--- | :--- | :--- | :--- |
| **`industrial-safety`** *(현재 기본값)* | 스마트 산업안전보건·위험성평가 엔지니어링 | 법적·공학적 엄밀성 + 현장 실무 중심 능동형 서술 | `docs/verified-facts.md` (산안법 제36조, 중처법 제4조, 하인리히 1:29:300, KRAS 5×5, `pdfplumber` 표 추출) |
| **`software-architecture`** | AI 에이전트·클라우드·시스템 엔지니어링 기술서 | 트레이드오프 중심(Why-First) + 실행 가능 코드 중심 | 아키텍처 대안 비교표 필수, 모든 코드 블록 `ast.parse` 무결성 및 버전 명시 |
| **`general-nonfiction`** | 기술 교양·비즈니스 전략·산업 트렌드 분석서 | 독자 공감형 스토리텔링 + 사례/통계 기반 논증 | 1차 통계 출처 인용 필수, 전문 용어 첫 등장 시 직관적 비유 병기 |

## 2. Why-First 프리셋 로딩 규칙
- 오케스트레이터와 `chapter-writer`는 `SKILL.md` 본문에 모든 장르의 문체 규칙을 하드코딩하지 않습니다. 모든 장르의 규칙을 상시 로드하면 현재 집필 중인 도서와 무관한 지침이 컨텍스트 예산을 잠식하기 **때문에**, `docs/toc.json`의 도서 주제에 맞는 프리셋만 Layer 3에서 선택적으로 참조합니다.
