# 📋 `book-writer` 7인 에이전트 오케스트레이션 하네스 구축 및 산업안전 도메인 집필 보고서

> **도서 제목**: 데이터와 AI로 구축하는 스마트 산업안전 엔지니어링 — 위험성평가부터 중대재해 예방 자동화까지 (`book_id: 20065`)  
> **1장 제목**: 스마트 산업안전보건과 데이터 기반 위험성평가 파이프라인 설계 (`manuscripts/chapter-01.md`)  
> **원격 저장소**: `https://github.com/woong-e/book-writer.git` (`main` 브랜치)  
> **참고 아키텍처**: [위키독스 클로드 코드 마스터북 (§book-writer)](https://wikidocs.net/363235) · [Harness Engineering 8 Principles](https://github.com/aiiiiiiiden/harness_engineering_8_priciples)

---

## 1. 프로젝트 디렉토리 구조 (`d:\projects\books`)

```text
books/
├── CLAUDE.md                                      # 전역 헌법 & 하네스 8대 원칙 (산업안전 도메인 반영)
├── SUBMISSION_REPORT.md                           # 수행 결과 캡처 및 다운로드용 종합 보고서
├── .claude/
│   ├── settings.json                              # Write/Edit 완료 시 verify.py 자동 실행 훅(Hooks)
│   ├── agents/                                    # [1단계] 7인 전문 안전 에이전트 정의 (최소 권한 & 모델 라우팅)
│   │   ├── researcher.md                          #   - 안전법규·재해사례 리서처 (opus, Write 허용)
│   │   ├── chapter-writer.md                      #   - 산업안전 원고 집필가 (opus, Write/Edit 허용, Web 차단)
│   │   ├── fact-checker.md                        #   - 산안법·중처법·KOSHA 팩트체커 (sonnet, Read-Only)
│   │   ├── tech-reviewer.md                       #   - 안전 코드·KRAS 계산 검토자 (opus, Read-Only)
│   │   ├── structure-reviewer.md                  #   - 구조·분량 검토자 (sonnet, Read-Only)
│   │   ├── proofreader.md                         #   - 산업안전 용어·AI 티 윤문자 (sonnet, Read-Only)
│   │   └── chapter-reviewer.md                    #   - 안전보건 총괄 비평가 (opus, Read-Only)
│   ├── commands/                                  # 슬래시 커맨드 단축키 (/write-chapter, /verify-all 등)
│   └── skills/
│       └── book-writer/
│           ├── SKILL.md                           # [2단계] 메타스킬 라우터 (250자 설명 + 7개 모드 분기)
│           ├── workflows/                         # 단계적 정보 공개(Progressive Disclosure) 워크플로
│           │   ├── 01-writing.md                  #   - 모드 1: 신규 챕터 집필 파이프라인
│           │   ├── 02-revision.md                 #   - 모드 2: 기존 원고 부분 개고
│           │   ├── 03-compile.md                  #   - 모드 3: 전체 원고 통합 컴파일
│           │   ├── 04-sampling-review.md          #   - 모드 4: 무작위 샘플링 품질 감사
│           │   ├── 05-consolidation.md            #   - 모드 5: 교차 챕터 용어·사실 통합
│           │   ├── 06-supervised-review.md        #   - 모드 6: 저자 감독형 대화식 리뷰
│           │   └── 07-paragraph-walkthrough.md    #   - 모드 7: 문단별 정밀 워크스루
│           └── references/                        # 참조 기준서
│               ├── style-guide.md                 #   - 문체 및 Why-First 작성 지침
│               ├── quality-checklist.md           #   - 4단계 품질 게이트 체크리스트
│               ├── glossary.md                    #   - 산업안전 및 하네스 표준 용어집 (12대 용어)
│               └── ai-tell-taxonomy.md            #   - 10대 AI 상투어(AI-Tell) 분류표
├── docs/                                          # 단일 진실 공급원 (System of Record)
│   ├── toc.json                                   #   - 스마트 산업안전 엔지니어링 목차 정의
│   ├── conventions.md                             #   - 집필 규약 및 필수 메타데이터 스키마
│   └── verified-facts.md                          #   - 산안법 제36조, 중처법 제4조, 하인리히 법칙, KRAS 등 검증 레지스트리
├── scripts/                                       # 기계적 품질 게이트 검증기 (Mechanical Enforcement)
│   ├── _harness.py                                #   - 공통 파서 및 어절 카운터
│   ├── status.py                                  #   - 챕터별 승인 현황 대시보드
│   ├── verify.py                                  #   - 메타데이터·분량(2,500~4,000단어)·AST 문법·금지어 검증
│   └── crosscheck.py                              #   - verified-facts.md 대조 및 교차검증 도장(crosscheck: pass) 발급
├── research/
│   └── chapter-01-notes.md                        # researcher가 작성한 1장 산업안전 리서치 노트
└── manuscripts/
    └── chapter-01.md                              # 7인 에이전트 파이프라인을 통과한 1장 최종 승인 원고 (3,513 단어)
```

---

## 2. 단계별 요구사항 구현 요약 (1단계 ~ 4단계)

### ✅ 1단계: 7인의 전문 에이전트 구성 및 최소 권한·모델 라우팅 (`.claude/agents/*.md`)
제임스 리즌의 **스위스 치즈 모델(Swiss Cheese Model)**과 보안 공학의 **최소 권한 원칙(Principle of Least Privilege)**을 결합하여 작성 주체(2인)와 읽기 전용 안전 검토 주체(5인)를 물리적으로 분리했습니다.

| 에이전트 파일 | 역할 구분 (산업안전 대응) | 할당 모델 | 허용 도구 (`tools`) | 차단 도구 (`disallowedTools`) |
| :--- | :--- | :---: | :--- | :--- |
| `researcher.md` | 안전법규·재해사례 리서처 | **`opus`** | `Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, SendMessage` | `Bash` |
| `chapter-writer.md` | 산업안전 원고 집필가 | **`opus`** | `Read, Write, Edit, Grep, Glob, SendMessage` | `Bash, WebSearch, WebFetch` |
| `fact-checker.md` | 산안법·중처법·통계 검증 | **`sonnet`** | `Read, Grep, Glob, WebSearch, WebFetch, SendMessage` | **`Write, Edit, Bash`** |
| `tech-reviewer.md` | 안전 코드·KRAS 계산 검토 | **`opus`** | `Read, Grep, Glob, SendMessage` | **`Write, Edit, Bash, WebSearch, WebFetch`** |
| `structure-reviewer.md` | 구조·분량(2,500~4,000단어) | **`sonnet`** | `Read, Grep, Glob, SendMessage` | **`Write, Edit, Bash, WebSearch, WebFetch`** |
| `proofreader.md` | 안전 용어·AI 티 윤문자 | **`sonnet`** | `Read, Grep, Glob, SendMessage` | **`Write, Edit, Bash, WebSearch, WebFetch`** |
| `chapter-reviewer.md` | 안전보건 총괄 비평·승인 | **`opus`** | `Read, Grep, Glob, SendMessage` | **`Write, Edit, Bash, WebSearch, WebFetch`** |

---

### ✅ 2단계: 오케스트레이터 스킬 (`SKILL.md`) 및 단계적 정보 공개
- **풍부한 트리거 키워드 설명문**: `.claude/skills/book-writer/SKILL.md`의 `description` 필드에 집필, 원고 수정, 팩트체크, 기술 감수, 윤문, 컴파일 등 약 250자 분량의 한국어 트리거 키워드를 촘촘히 배치했습니다.
- **단계적 정보 공개 (Progressive Disclosure)**: `SKILL.md`는 7가지 작업 모드(`writing`, `revision`, `compile`, `sampling-review`, `consolidation`, `supervised-review`, `paragraph-walkthrough`)를 분기하는 라우팅 테이블만 유지하고, 상세 절차는 `workflows/01-writing.md` ~ `07-paragraph-walkthrough.md`를 필요한 시점에 조건부 로드하여 컨텍스트 예산을 보호합니다.

---

### ✅ 3단계: 파이프라인 실행 흐름 및 P2P 소통 프로토콜 (`SendMessage`)
- **우체국 안티패턴(Post-Office Anti-Pattern) 배제**: 오케스트레이터가 중간에서 일산화탄소 노출기준(TWA `30 ppm`, STEL `200 ppm`)이나 코드 결함 행 번호를 대리 요약하지 않고, 에이전트들이 `SendMessage`로 직접 정밀 사양과 수정 제안을 주고받았습니다.
- **실행 파이프라인**:
  ```text
  [1. 리서치] researcher ──(SendMessage: research/chapter-01-notes.md)──▶ [2. 초고 집필] chapter-writer
        │
        ▼ (SendMessage 병렬 검증 요청)
  [3. 3인 병렬 안전 방어선] fact-checker ∥ tech-reviewer ∥ structure-reviewer
        │
        ▼ (1차 개고 완료 후 SendMessage)
  [4. 용어·문장 윤문] proofreader ──(교정표 직송)──▶ chapter-writer (humanized: "pass")
        │
        ▼ (SendMessage 최종 감수 요청)
  [5. 최종 출판 승인] chapter-reviewer ──▶ status: "approved" 도장 부여
  ```

---

### ✅ 4단계: 산업안전 도메인 품질 게이트 및 Why-First 코드 검증
1. **산업안전 핵심 법령·이론 반영 (`docs/verified-facts.md` 일치)**:
   - **산업안전보건법 제36조(위험성평가의 실시)**: 사전준비 → 유해·위험요인 파악 → 위험성 추정 → 위험성 결정 → 감소대책 수립·실행 → 기록·공유 (6단계)
   - **중대재해처벌법 제4조**: 경영책임자의 안전보건관리체계 구축 및 이행 의무
   - **하인리히의 1:29:300 법칙**: 중상 1건 : 경상 29건 : **아차사고(Near-Miss)** 300건 데이터 기록 시스템화
   - **제임스 리즌의 스위스 치즈 모델 & 위험 통제 5단계 계층**: `1단계 제거 → 2단계 대체 → 3단계 공학적 대책 → 4단계 관리적 대책 → 5단계 개인보호구(PPE)` 우선순위 강제
   - **안전보건공단(KOSHA) KRAS 5×5 매트릭스**: $\text{가능성(1~5)} \times \text{중대성(1~5)} \ge 8$점 시 '허용 불가 위험' 판정 및 PPE 단독 대책 승인 차단
2. **Why-First 원칙 (`pdfplumber` vs `PyPDF2`)**:
   - **물질안전보건자료(MSDS)** 제8항 노출기준 표 및 작업환경측정 결과표 PDF 추출 시, 단순 텍스트 스트림만 읽어 셀 경계가 무너지는 레거시 `PyPDF2`(`v3.0.1` Deprecated) 대신 $(x_0, top, x_1, bottom)$ 바운딩 박스 좌표를 계산하는 `pdfplumber`(`v0.11.x`)를 사용하는 이유와 인메모리 PDF 실행 코드를 수록했습니다.

---

## 3. 기계적 품질 게이트 실행 결과 (캡처용 터미널 출력)

```text
PS D:\projects\books> python scripts/crosscheck.py --facts
PASS ✅ (docs/verified-facts.md 레지스트리 무결성 확인 완료)

PS D:\projects\books> python scripts/crosscheck.py chapter-01
[CROSSCHECK] chapter-01 교차검증 완료: 총 9건 점검, 차단급 오류 0건
  ✅ [low] 에이전트 'researcher' 역할 및 모델('opus') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'chapter-writer' 역할 및 모델('opus') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'fact-checker' 역할 및 모델('sonnet') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'tech-reviewer' 역할 및 모델('opus') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'structure-reviewer' 역할 및 모델('sonnet') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'proofreader' 역할 및 모델('sonnet') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] 에이전트 'chapter-reviewer' 역할 및 모델('opus') 정의 일관성 (docs/verified-facts.md §3 7인 에이전트 매트릭스 일치)
  ✅ [low] PDF 테이블 추출 시 PyPDF2 대신 pdfplumber를 사용하는 기술적 이유(Why-First) 명시 (docs/verified-facts.md §1 pdf_table_extraction_rule 일치)
  ✅ [low] 산업안전보건법 제36조(위험성평가) 및 하인리히 1:29:300 법칙 정확성 (docs/verified-facts.md §1 산업안전 핵심 법령·이론 표 일치)
front-matter 도장 갱신: crosscheck=pass, crosscheck_date=2026-11-10
PASS ✅

PS D:\projects\books> python scripts/status.py
[BOOK] 데이터와 AI로 구축하는 스마트 산업안전 엔지니어링 — 위험성평가부터 중대재해 예방 자동화까지  (book_id=20065)

■ 1부. 스마트 산업안전보건과 위험성평가 엔지니어링
  ✔ [1] 스마트 산업안전보건과 데이터 기반 위험성평가 파이프라인 설계 (chapter-01)  <approved>  words=3513  crosscheck=pass  humanized=pass
  ✗ [2] 화학물질 안전관리(MSDS)와 작업환경측정 데이터 자동 파싱 (chapter-02)  (파일 없음)
  ✗ [3] 중대재해처벌법 안전보건관리체계와 아차사고(Near-Miss) 피드백 루프 (chapter-03)  (파일 없음)

────────────────────────────────────────────────────────────────────────
합계 3장  |  ✔ approved:1  |  ✗ missing:2
검증·승인 완료 진척률: 1/3 (33%)

PS D:\projects\books> python scripts/verify.py
[WARN]  chapter-02: toc.json에 등록되어 있으나 원고 파일 없음 (`python scripts/scaffold.py` 실행 권장)
[WARN]  chapter-03: toc.json에 등록되어 있으나 원고 파일 없음 (`python scripts/scaffold.py` 실행 권장)

──────────────────────────────────────────────────
검증 결과: errors 0 · warnings 2
PASS ✅ (모든 기계적 불변식 및 품질 게이트 통과)
```
