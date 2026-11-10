# 검증된 핵심 사실 레지스트리 (Single Source of Truth — 산업안전보건 도메인)

> 이 책 전체에서 반복 등장하는 **산업안전보건 법령·이론·통계·데이터 파싱 규격 및 7인 에이전트 아키텍처 정의**의 단일 진실의 원천(SoT)이다.
> 모든 장은 이 표와 일치해야 한다. 불일치는 버그다 → `fact-checker` 에이전트 및 `scripts/verify.py`, `scripts/crosscheck.py`가 자동 검출한다.
> 사실이 바뀌면 **여기를 먼저 고치고**, 그 다음 본문을 고친다.
> 마지막 검증일: 2026-11-10

---

## 1. 산업안전보건 핵심 법령·이론 사실 표

| key | 값 | 근거 / 비고 |
| :--- | :--- | :--- |
| `osh_act_risk_assessment` | **산업안전보건법 제36조(위험성평가의 실시)** | 사업주는 건설물, 기계·기구·설비, 원재료, 가스, 증기, 분진, 근로자의 작업행동 또는 그 밖의 업무로 인한 유해·위험요인을 찾아내어 부상 및 질병으로 이어질 수 있는 위험성의 크기가 허용 가능한 범위인지를 평가하여야 하고, 그 결과에 따라 조치를 하여야 함 (출처: `https://www.law.go.kr/`) |
| `sapa_act_article_4` | **중대재해 처벌 등에 관한 법률(중대재해처벌법) 제4조** | 사업주와 경영책임자등의 안전 및 보건 확보의무 — 재해예방에 필요한 인력 및 예산 등 안전보건관리체계의 구축 및 그 이행에 관한 조치 규정 |
| `heinrich_law` | **하인리히 법칙 (Heinrich's Law, 1:29:300 법칙)** | 허버트 윌리엄 하인리히(H. W. Heinrich, 1931)의 *Industrial Accident Prevention*: 중상 또는 사망 재해 **1건**이 발생하기 전, 같은 원인으로 발생한 경미한 사고 **29건**과 부상은 없었으나 아찔했던 **아차사고(Near-Miss) 300건**이 선행한다는 통계적 법칙 |
| `swiss_cheese_model` | **제임스 리즌의 스위스 치즈 모델 (Swiss Cheese Model)** | 제임스 리즌(James Reason, 1990)의 다중 방어선 이론: 설비적 방호장치, 표준안전작업절차(SOP), 작업허가제(PTW), 개인보호구(PPE) 등 여러 방어선(치즈 슬라이스)의 구멍(결함)이 일직선으로 정렬될 때 중대재해가 발생함 |
| `hierarchy_of_controls` | **위험 통제 5단계 계층 (Hierarchy of Controls — NIOSH/ISO 45001)** | **1단계 제거(Elimination) → 2단계 대체(Substitution) → 3단계 공학적 대책(Engineering Controls) → 4단계 관리적 대책(Administrative Controls) → 5단계 개인보호구(PPE)** 순서로 위험 감소 대책을 우선 수립해야 함 |
| `krish_risk_matrix` | **위험성(Risk) 산출 공식 (KRAS 표준 모델)** | $\text{위험성(Risk)} = \text{가능성(빈도, Likelihood/Frequency)} \times \text{중대성(강도, Severity)}$. 5×5 매트릭스 기준(1~25점)에서 통상 **8점 이상**은 허용 불가 위험으로 분류하여 즉시 감소 대책을 수립함 (출처: 안전보건공단 KRAS 지침 `https://www.kosha.or.kr/`) |
| `pdf_table_extraction_rule` | 산업안전 문서(MSDS 16개 항목 표, 작업환경측정 결과표, 위험성평가표)의 PDF 테이블 추출에는 **`pdfplumber`**(`v0.11.x`)를 사용한다 | **`PyPDF2`**(`v3.0.1` 이후 Deprecated)는 단순 텍스트 스트림 추출에 특화되어 표의 셀 경계(화학물질명·CAS 번호·노출기준 TWA/STEL 열)와 레이아웃 구조를 보존하지 못하기 때문 (Why-First 원칙 대표 사례) |

---

## 2. 스마트 산업안전 엔지니어링 5대 핵심 원칙 (전 장 통일)

| # | 원칙 명칭 | 핵심 내용 (산업안전 현장 적용) |
| :--- | :--- | :--- |
| 1 | **아차사고(Near-Miss) 데이터 기록 시스템화** | 1:29:300 법칙에 따라 현장의 사소한 아차사고와 위험요인을 휘발성 구두 보고가 아닌 구조화된 저장소(System of Record)에 기록한다 |
| 2 | **작업환경 및 유해인자 가독성 확보** | MSDS(물질안전보건자료), 작업환경측정 PDF, IoT 가스·온열 센서 데이터를 기계와 안전 에이전트가 즉시 파싱 가능한 정형 데이터로 변환한다 |
| 3 | **다중 방어선(Swiss Cheese)과 최소 권한 통제** | 위험작업 허가(PTW)와 안전 점검에서 작성자(작업자/시공팀)와 승인·검토자(안전관리자)의 권한을 분리하여 셀프 승인을 원천 차단한다 |
| 4 | **위험성평가 및 법규 검증의 기계적 강제** | 빈도×강도 계산, 노출기준(TWA/STEL) 초과 여부, 법정 필수 항목 누락을 사람의 눈대중이 아닌 코드(`verify.py`)로 기계적으로 검증한다 |
| 5 | **지속적 위험 감소 자율 피드백 루프** | `유해위험요인 발굴 → 위험성 추정 → 감소대책 수립(제거·대체·공학적·관리적·PPE) → 잔여 위험성 재평가` 루프를 상시 가동한다 |

---

## 3. 7인 에이전트 역할·모델 라우팅·최소 권한 매트릭스 (SoT)

| 에이전트명 (`.claude/agents/`) | 역할 구분 | 모델 (`model`) | 허용 도구 (`tools`) | 차단 도구 (`disallowedTools`) |
| :--- | :--- | :--- | :--- | :--- |
| **`researcher`** | 작성 (안전법규·재해사례 조사) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Bash` |
| **`chapter-writer`** | 작성 (산업안전 원고 초고·개고) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `SendMessage` | `Bash`, `WebSearch`, `WebFetch` |
| **`fact-checker`** | 검토 (산안법·KOSHA 통계 검증) | `sonnet` | `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Write`, `Edit`, `Bash` |
| **`tech-reviewer`** | 검토 (안전 데이터·코드 검토) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`structure-reviewer`** | 검토 (구조·분량 2,500~4,000단어) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`proofreader`** | 검토 (산업안전 용어·AI 티 윤문) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`chapter-reviewer`** | 검토 (안전보건 총괄 비평·승인) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |

---

## 4. 금지 표현 (denylist) — `scripts/verify.py` 기계적 차단

| 금지 패턴 | 이유 | 올바른 표현 |
| :--- | :--- | :--- |
| `하인리히의 1:30:300 법칙`, `1:10:300 법칙` | 통계 수치 오류 — 하인리히 법칙의 정확한 비율은 1:29:300임 | **"하인리히의 1:29:300 법칙"** |
| `개인보호구(PPE)를 최우선 대책으로` | 위험 통제 계층(Hierarchy of Controls) 위반 — PPE는 최후의 방어선(5단계)임 | **"제거·대체·공학적 대책을 우선 적용하고 개인보호구(PPE)는 최후의 보루로 적용"** |
| ` 산업안전보건법 제4조에 따른 위험성평가` | 법 조항 착오 (산안법상 위험성평가는 제36조, 중대재해처벌법상 안전보건확보의무가 제4조임) | **"산업안전보건법 제36조(위험성평가)"** / **"중대재해처벌법 제4조"** |
| `docs.claude.com/docs` | 구 도메인 | `code.claude.com/docs` |
| `정본` | 독자 대상 용어 통일 규칙 | `원문` 또는 `공식 지침` |
