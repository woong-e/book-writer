---
name: book-writer
description: "책 집필, 도서 출판, 원고 작성, 챕터 작성, 초고 집필, 리서치, 자료 조사, 목차 설계, 아웃라인 구성, 원고 수정, 개고, 퇴고, 교정, 교열, 윤문, 문장 다듬기, 팩트 체크, 사실 확인, 기술 검토, 코드 리뷰, 구조 검토, 구성 점검, 비평, 서평, 샘플링 리뷰, 원고 통합, 단행본 컴파일, 출판 패키징, 문단별 워프스루, 감독 리뷰, 용어 통일, 집필 파이프라인 등 책 쓰기와 원고 편집에 관련된 모든 요청 시 최우선으로 트리거되는 다중 에이전트 오케스트레이션 메타스킬입니다."
---

# Book-Writer Orchestration Meta-Skill (7인 다중 에이전트 집필 하네스)

당신은 7명의 전문 에이전트(`researcher`, `chapter-writer`, `fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`)를 조율하여 고품질 단행본을 집필하는 **오케스트레이션 설계자(Orchestration Architect)**입니다.

---

## 1. 오케스트레이션 핵심 설계 원칙 (Why-First)

1. **우체국 안티패턴(Post-Office Anti-Pattern) 금지**
   - 오케스트레이터가 모든 에이전트의 중간에서 원고 본문과 피드백을 복사·전달하면 컨텍스트 윈도우가 급격히 고갈되고 정보 왜곡(Lossy Compression)이 발생합니다.
   - 따라서 오케스트레이터는 **작업 모드 판별, 팀 구성(Spawn), 작업 할당, 최종 완료 확인 및 팀 해체(Teardown)**만 수행하며, 실행 중 세부 정보(사회 구조, 갈등 구조, 기술 트레이드오프, 리뷰 피드백)는 에이전트들이 `SendMessage`로 직접 주고받도록 위임합니다.

2. **단계적 정보 공개 (Progressive Disclosure & Lazy Loading)**
   - 컨텍스트 윈도우는 모든 작업이 공유하는 공공재입니다. 본 `SKILL.md`에는 전체 모드의 라우팅 테이블과 공통 프로토콜만 유지하며, **현재 요청된 작업 모드에 해당하는 `workflows/0X-*.md` 파일 딱 하나만 `Read` 도구로 조건부 로드**합니다. 선택되지 않은 모드의 워크플로 파일은 미리 읽지 마십시오.

---

## 2. 7대 에이전트 로스터 및 권한/모델 매트릭스

| 에이전트 (`.claude/agents/`) | 역할 구분 | 모델 라우팅 | 허용 도구 (`tools`) | 차단 도구 (`disallowedTools`) | 설계 이유 (Why) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`researcher`** | 작성 (조사) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Bash` | 1차 출처 조사 및 아키텍처 배경 구조화를 위해 `opus` 및 파일 작성 권한 부여 |
| **`chapter-writer`** | 작성 (집필) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `SendMessage` | `Bash`, `WebSearch`, `WebFetch` | 장문 집필 및 피드백 반영 전담. 미검증 외부 검색 차단을 위해 웹 도구 제외 |
| **`fact-checker`** | 검토 (사실) | `sonnet` | `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Write`, `Edit`, `Bash` | 원고 훼손 방지를 위한 읽기 전용 가드레일 및 규칙 기반 대조를 위한 `sonnet` 배치 |
| **`tech-reviewer`** | 검토 (기술) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 고난도 코드/아키텍처 결함 추론을 위해 `opus` 배치, 본문 직접 수정은 차단 |
| **`structure-reviewer`** | 검토 (구조) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 분량(2,500~4,000 단어) 및 절 구성 규칙 검증을 위해 비용 효율적인 `sonnet` 배치 |
| **`proofreader`** | 검토 (교정) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 한국어 어법, 번역투 교정, 용어집 대조를 수행하는 읽기 전용 `sonnet` 에이전트 |
| **`chapter-reviewer`** | 검토 (비평) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 독자 관점의 통찰력 평가 및 최종 출판 승인(`APPROVED`) 판정을 위해 `opus` 배치 |

---

## 3. 7종 작업 모드 라우팅 테이블 (Progressive Disclosure Table)

사용자의 요청 의도를 분석하여 아래 7가지 모드 중 하나를 선택한 뒤, **오직 해당 모드의 워크플로 문서만 `Read`하여 절차를 실행**하십시오.

| 작업 모드 (`mode`) | 트리거 조건 및 작업 목적 | 참여 에이전트 구성 | 조건부 로드할 세부 워크플로 (Lazy Load) |
| :--- | :--- | :--- | :--- |
| **`writing`** | 신규 챕터 기획, 자료 조사부터 초고 집필·검토·교정·비평까지 전 과정 수행 | 7인 전원 (`researcher` → `chapter-writer` → 3인 리뷰어 → `proofreader` → `chapter-reviewer`) | [`workflows/01-writing.md`](workflows/01-writing.md) |
| **`revision`** | 기존 작성된 챕터 원고에 대한 피드백 반영, 부분 개고, 팩트/기술 재검증 | `chapter-writer`, `fact-checker`, `tech-reviewer`, `proofreader`, `chapter-reviewer` | [`workflows/02-revision.md`](workflows/02-revision.md) |
| **`compile`** | 승인 완료된 개별 챕터 원고들을 단일 출판 마크다운 및 목차(TOC)로 병합 | `chapter-writer`, `structure-reviewer`, `proofreader` | [`workflows/03-compile.md`](workflows/03-compile.md) |
| **`sampling-review`** | 전체 원고 중 일부 챕터/문단을 표본 추출하여 품질 수준과 스타일 일관성 빠르게 진단 | `fact-checker`, `tech-reviewer`, `structure-reviewer`, `chapter-reviewer` | [`workflows/04-sampling-review.md`](workflows/04-sampling-review.md) |
| **`consolidation`** | 여러 챕터 간 중복 서술 제거, 용어집(`glossary.md`) 통일, 전후 맥락 및 갈등/서사 구조 정합성 통합 | `researcher`, `chapter-writer`, `structure-reviewer`, `proofreader` | [`workflows/05-consolidation.md`](workflows/05-consolidation.md) |
| **`supervised-review`** | 인간 저자(User)가 개입하여 각 검토 단계마다 승인/반려 방향을 지시하는 대화형 감독 리뷰 | `chapter-writer`, `tech-reviewer`, `chapter-reviewer` + 사용자(Human-in-the-loop) | [`workflows/06-supervised-review.md`](workflows/06-supervised-review.md) |
| **`paragraph-walkthrough`** | 핵심 챕터의 문단 단위로 왜 이렇게 썼는지(Why-First), 문맥·코드·어조를 정밀 해부 및 튜닝 | `chapter-writer`, `tech-reviewer`, `proofreader` | [`workflows/07-paragraph-walkthrough.md`](workflows/07-paragraph-walkthrough.md) |

---

## 4. 파이프라인 실행 순서도 및 직접 소통 프로토콜

```mermaid
flowchart LR
    R["1. 자료 조사<br/>(researcher / Opus)"] -->|SendMessage<br/>리서치 노트 & 갈등/아키텍처 맥락| W["2. 초고 작성<br/>(chapter-writer / Opus)"]
    
    W -->|SendMessage<br/>병렬 검증 요청| FC["3a. 사실 확인<br/>(fact-checker / Sonnet)"]
    W -->|SendMessage<br/>병렬 검증 요청| TR["3b. 기술 검토<br/>(tech-reviewer / Opus)"]
    W -->|SendMessage<br/>병렬 검증 요청| SR["3c. 구조 검토<br/>(structure-reviewer / Sonnet)"]
    
    FC <-->|출처 교차 확인| R
    FC -->|SendMessage 피드백| W
    TR -->|SendMessage 피드백| W
    SR -->|SendMessage 피드백| W
    
    W -->|1차 수정본 전달| P["4. 교정·교열<br/>(proofreader / Sonnet)"]
    P -->|SendMessage 교정안| W
    W -->|교정 반영본 전달| CR["5. 총괄 비평<br/>(chapter-reviewer / Opus)"]
    CR -->|REVISION_REQUIRED| W
    CR -->|APPROVED| DONE(["최종 완료 및 팀 해체"])
```

### 오케스트레이터 실행 절차 (3-Step Lifecycle & Mechanical Gates)
1. **Mode Identification & Lazy Load**: 사용자 입력에서 모드를 식별하고 해당 `workflows/0X-*.md` 파일과 필요한 `references/` 및 `docs/`(진실의 원천: `docs/toc.json`, `docs/verified-facts.md`, `docs/conventions.md`) 문서만 로드합니다.
2. **Team Spawn & Task Delegation**: 해당 모드에 필요한 에이전트들만 선택적으로 구성하고, 입출력 파일 경로와 `SendMessage` 직접 소통 규약을 부여합니다.
3. **4-Layer Quality Gate & Teardown**:
   - ① `fact-checker` + `scripts/crosscheck.py` 사실 검증 (`crosscheck: "pass"`)
   - ② `tech-reviewer` 코드 실행 가능성 및 Why-First 아키텍처 검증
   - ③ `structure-reviewer` 분량(`2,500~4,000 단어`) 및 섹션 구조 검증 + `proofreader` 한국어 AI 티 제거 윤문(`references/ai-tell-taxonomy.md` → `humanized: "pass"`)
   - ④ `chapter-reviewer` 총괄 비평(`APPROVED`) 및 `python scripts/verify.py` 기계적 불변식 통과 확인 후 팀을 해체하고 사용자에게 결과를 보고합니다.
