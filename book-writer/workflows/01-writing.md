# Workflow 01: Writing Mode (신규 챕터 전 과정 집필 파이프라인)

> **Lazy Load Notice**: 이 문서는 사용자가 **신규 챕터 집필(`writing`)**을 요청했을 때만 로드됩니다.

## 1. 파이프라인 아키텍처 (Execution Flow)

`자료 조사(researcher)` ➔ `초고 작성(chapter-writer)` ➔ `[사실 확인(fact-checker) | 기술 검토(tech-reviewer) | 구조 검토(structure-reviewer)]` ➔ `교정(proofreader)` ➔ `비평(chapter-reviewer)`

---

## 2. 단계별 실행 및 직접 소통(`SendMessage`) 프로토콜

### Step 1: 자료 조사 (`researcher` - Opus)
1. 오케스트레이터가 `researcher`에게 대상 챕터 주제와 목표 독자층을 전달합니다.
2. `researcher`는 공식 문서 및 학술 자료를 조사하여 `research/chapter-XX-notes.md`를 작성합니다.
3. **[직접 소통]**: `researcher`는 오케스트레이터를 거치지 않고 `SendMessage`를 통해 `chapter-writer`에게 다음 정보를 직접 브리핑합니다:
   - 리서치 노트 파일 경로
   - 다뤄야 할 핵심 기술/이론의 등장 배경(Why)과 아키텍처 트레이드오프
   - 서사적 갈등 구조(기존 방식의 한계 vs 새로운 패러다임의 해결 방식) 및 도메인 맥락

### Step 2: 초고 집필 (`chapter-writer` - Opus)
1. `chapter-writer`는 `references/style-guide.md`를 읽고 `research/chapter-XX-notes.md`를 바탕으로 `manuscripts/chapter-XX.md` 초고를 작성합니다.
2. **제출 전 자기 점검 (Self-Verification)**:
   - 상단에 `<!-- chapter: XX, title: "...", word_count: NNNN, status: draft -->` 메타데이터 주석 포함
   - 본문 분량 **2,500~4,000 단어** 충족 확인
   - 모든 코드 블록 실행 가능 여부 및 Why-First 설명 구조 확인
3. **[직접 소통]**: 초고 완료 즉시 `SendMessage`로 `fact-checker`, `tech-reviewer`, `structure-reviewer` 3인에게 동시에 검토를 요청합니다.

### Step 3: 3인 병렬 검증 (`fact-checker`, `tech-reviewer`, `structure-reviewer`)
세 에이전트는 모두 **읽기 전용(`Write`, `Edit` 차단)**으로 원고를 병렬 분석합니다:
- **`fact-checker` (Sonnet)**: 수치, 연도, 인용구의 사실 여부 검증. 의문점은 `researcher`와 `SendMessage`로 직접 교차 확인 후, 수정 요청을 `chapter-writer`에게 전송.
- **`tech-reviewer` (Opus)**: 코드 블록 실행 가능성, 엣지 케이스, 아키텍처 타당성 검증 후 `chapter-writer`에게 대안 코드 스니펫과 이유(Why)를 전송.
- **`structure-reviewer` (Sonnet)**: 2,500~4,000 단어 분량 준수, 절 간 호흡, 선행 지식 역전 여부를 점검하여 `chapter-writer`에게 전송.

### Step 4: 1차 개고 및 교정·교열 (`chapter-writer` ➔ `proofreader` - Sonnet)
1. `chapter-writer`는 3인의 피드백을 종합하여 원고를 수정(`status: revised`)한 뒤 `proofreader`에게 `SendMessage`로 교정을 요청합니다.
2. `proofreader`는 맞춤법, 번역투 문장, `references/glossary.md` 용어 통일성을 검사하여 수정 전후 비교표를 `chapter-writer`에게 회신합니다.
3. `chapter-writer`가 문장 교정을 반영합니다.

### Step 5: 총괄 비평 및 품질 게이트 (`chapter-reviewer` - Opus)
1. `chapter-reviewer`는 교정 완료본을 통독하며 독자 몰입감, 통찰력, 체크리스트 달성 여부를 최종 감사(Audit)합니다.
2. 미비점이 있으면 `SendMessage`로 `chapter-writer`에게 재수정을 지시(`REVISION_REQUIRED`)하고, 기준 충족 시 `APPROVED` 사인을 오케스트레이터에게 보고합니다.
3. 오케스트레이터는 최종 상태를 확인하고 집필 팀을 해체합니다.
