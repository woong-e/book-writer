# 🔍 `antipattern-detector` 기반 `book-writer/SKILL.md` 3대 안티패턴 진단 보고서

> **진단 에이전트**: [`antipattern-detector.md`](file:///d:/projects/books/.claude/agents/antipattern-detector.md) ([`revfactory/harness-engineering-with-cc/ex-05-12-antipatterns`](https://github.com/revfactory/harness-engineering-with-cc/tree/main/ex-05-12-antipatterns))  
> **진단 대상**: [`.claude/skills/book-writer/SKILL.md`](file:///d:/projects/books/.claude/skills/book-writer/SKILL.md) (및 `references/`, `workflows/` 서브시스템)  
> **진단 일시**: 2026-11-10  

---

## 1. 핵심 요약 테이블 (캡처 제출용 요약)

| 안티패턴 구분 | `antipattern-detector` 진단 룰 | 실측 수치 (`wc` / `grep` / `ls`) | 발현 여부 | 심각도 (`low`/`med`/`high`) | 해결 권고 및 아키텍처 매핑 (`cross-ref`) |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **안티패턴 1<br/>(거대 본문)** | `wc -l >= 500` 이면 발현 | **`wc -l` = 82행** (8,815 Bytes)<br/>*(임계치 500행 대비 16.4%)* | **`no` (미발현)** | **`low`** | **[Progressive Disclosure 적용 완료]**<br/>메인 `SKILL.md`는 82행 라우팅 허브로 유지하고 7개 모드 세부 절차는 `workflows/01~07-*.md`로 조건부 로드(Lazy Load)함. 향후 모드 추가 시에도 150행 이하 유지 권고. |
| **안티패턴 2<br/>(`references` 부재)** | `references/` 디렉토리 없음<br/>`+` 본문 도메인 분기 `>= 4` 이면 발현 | **`references/` 존재 (`True`, 4종 파일)**<br/>`+` 본문 도메인 분기 **7개** (`writing` 등) | **`no` (미발현)** | **`low`** | **[Layer 3 References 분리 완료]**<br/>도메인 분기(7개 모드)에 필요한 스타일 가이드, 품질 체크리스트, 용어집, AI 티 분류표를 `references/` 하위 4개 파일로 격리 완료. 향후 장르별 프리셋 확장 시 하위 폴더 구조화 권고. |
| **안티패턴 3<br/>(이유 없는 규칙)** | `grep -c 'ALWAYS\|NEVER\|반드시\|절대' >= 5`<br/>`AND` `grep -c '왜냐하면\|때문에' == 0` 이면 발현 | 억압적 강제어(`ALWAYS/NEVER/반드시/절대`): **0건**<br/>인과 키워드(`때문에`): **2건** + 전용 `설계 이유 (Why)` 칼럼 **7건** | **`no` (미발현)** | **`low`** | **[Why-First 원칙 적용 완료]**<br/>무조건적 강제어(0건) 대신 우체국 안티패턴(정보 손실·컨텍스트 고갈) 및 7인 에이전트 도구·모델 라우팅의 기술적 이유(Why)를 인과적으로 명시함. 향후 추가 규칙에도 Why-First 서술 유지 권고. |

---

## 2. 터미널 실측 로그 (`wc` / `grep` / 디렉토리 검증)

```text
PS D:\projects\books> # [Rule 1] SKILL.md 라인 수 실측 (wc -l >= 500 검사)
PS D:\projects\books> (Get-Content .claude/skills/book-writer/SKILL.md).Count
82

PS D:\projects\books> # [Rule 2] references/ 디렉토리 및 workflows/ 분리 실측
PS D:\projects\books> Get-ChildItem .claude/skills/book-writer/references/, .claude/skills/book-writer/workflows/ | Select-Object Directory, Name, @{N='Lines';E={(Get-Content $_.FullName).Count}}

Directory                                                 Name                         Lines
---------                                                 ----                         -----
D:\projects\books\.claude\skills\book-writer\references   ai-tell-taxonomy.md             27
D:\projects\books\.claude\skills\book-writer\references   glossary.md                     18
D:\projects\books\.claude\skills\book-writer\references   quality-checklist.md            41
D:\projects\books\.claude\skills\book-writer\references   style-guide.md                  29
D:\projects\books\.claude\skills\book-writer\workflows    01-writing.md                   43
D:\projects\books\.claude\skills\book-writer\workflows    02-revision.md                  20
D:\projects\books\.claude\skills\book-writer\workflows    03-compile.md                   17
D:\projects\books\.claude\skills\book-writer\workflows    04-sampling-review.md           17
D:\projects\books\.claude\skills\book-writer\workflows    05-consolidation.md             17
D:\projects\books\.claude\skills\book-writer\workflows    06-supervised-review.md         16
D:\projects\books\.claude\skills\book-writer\workflows    07-paragraph-walkthrough.md     18

PS D:\projects\books> # [Rule 3] 강제어(ALWAYS|NEVER|반드시|절대) vs 인과·Why-First 근거 실측
PS D:\projects\books> (Select-String -Path .claude/skills/book-writer/SKILL.md -Pattern "ALWAYS|NEVER|반드시|절대").Count
0
PS D:\projects\books> (Select-String -Path .claude/skills/book-writer/SKILL.md -Pattern "왜냐하면|때문에").Count
2
PS D:\projects\books> (Select-String -Path .claude/skills/book-writer/SKILL.md -Pattern "Why-First|설계 이유|위해").Count
9
```

---

## 3. 안티패턴별 상세 진단 및 해결 권고

### ① 안티패턴 1: 거대 본문 (Monolithic `SKILL.md`)
- **발현 여부**: **`no` (미발현)**
- **심각도**: **`low`** (모니터링 수준, 양호)
- **근거 (실측 수치)**:
  - `wc -l` 실측 결과 **82행**(8,815 Bytes)으로, 거대 본문 안티패턴 발현 임계치인 `500행`의 **16.4%** 수준입니다.
  - 7가지 작업 모드의 상세 실행 절차를 본문에 나열하지 않고 `workflows/01-writing.md` ~ `07-paragraph-walkthrough.md`(합계 148행)로 분리했습니다.
- **해결 및 유지 권고 (`cross-ref`: Progressive Disclosure)**:
  - 현재 적용된 **단계적 정보 공개(Progressive Disclosure)** 구조를 유지하십시오. 신규 워크플로 모드가 추가되더라도 `SKILL.md`의 섹션 3 라우팅 테이블에는 1행만 추가하고, 상세 프롬프트는 `workflows/08-*.md`로 외부화하여 메인 `SKILL.md`가 항상 150행 미만을 유지하도록 관리합니다.

### ② 안티패턴 2: `references` 부재 (Missing Layer 3 References)
- **발현 여부**: **`no` (미발현)**
- **심각도**: **`low`** (모니터링 수준, 양호)
- **근거 (실측 수치)**:
  - 본문 내 도메인 작업 분기가 **7개**(`writing`, `revision`, `compile`, `sampling-review`, `consolidation`, `supervised-review`, `paragraph-walkthrough` ≥ 4)로 다양하지만, `.claude/skills/book-writer/references/` 디렉토리가 존재하며 4종의 핵심 기준 문서(`style-guide.md`, `quality-checklist.md`, `glossary.md`, `ai-tell-taxonomy.md`)로 총 115행의 도메인 규칙이 분리되어 있습니다.
- **해결 및 유지 권고 (`cross-ref`: Layer 3 분리)**:
  - 도메인 지식과 평가 체크리스트를 `references/`(Layer 3)와 `docs/verified-facts.md`(단일 진실 공급원)에 격리한 현행 설계를 유지하십시오. 향후 도서 도메인(예: 산업안전, 클라우드, 금융 등)이 다변화될 경우 `references/domains/` 하위 디렉토리를 두어 도메인별 용어집을 선택 로드하도록 확장할 것을 권고합니다.

### ③ 안티패턴 3: 이유 없는 규칙 (Unjustified Rules / Why-First 위반)
- **발현 여부**: **`no` (미발현)**
- **심각도**: **`low`** (모니터링 수준, 양호)
- **근거 (실측 수치)**:
  - 맥락 없이 에이전트를 억압하는 강제 키워드(`ALWAYS`, `NEVER`, `반드시`, `절대`)가 **0건**(`grep -c` = 0 < 5)이며, 인과 키워드(`때문에`) **2건** 및 Why-First 설계 근거가 **9건** 명시되어 있습니다.
  - 섹션 1(`## 1. 오케스트레이션 핵심 설계 원칙 (Why-First)`)에서 우체국 안티패턴 금지 이유(*"컨텍스트 윈도우가 급격히 고갈되고 정보 왜곡(Lossy Compression)이 발생하기 때문에"*)와 단계적 정보 공개 이유(*"컨텍스트 윈도우는 모든 작업이 공유하는 공공재이기 때문에"*)를 설명했고, 섹션 2의 7대 에이전트 매트릭스에 **`설계 이유 (Why)` 전용 열**을 두어 각 에이전트의 도구 제한(`disallowedTools`)과 모델 배치(`opus` vs `sonnet`) 근거를 구체적으로 서술했습니다.
- **해결 및 유지 권고 (`cross-ref`: Why-First)**:
  - 새로운 제약이나 에이전트 규칙을 추가할 때도 `NEVER`·`반드시` 같은 단정적 금지어 대신 **"실패 시 발생하는 부작용(Why) → 권장 행동"** 구조를 일관되게 유지하십시오.
