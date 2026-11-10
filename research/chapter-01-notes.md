<!-- chapter: 01, target_version: 1.0, status: verified -->

# 1장 리서치 노트: 스마트 산업안전보건과 데이터 기반 위험성평가 파이프라인 설계

> **작성자**: `researcher` (수석 리서처, Opus)  
> **대상 챕터**: 1장 — 스마트 산업안전보건과 데이터 기반 위험성평가 파이프라인 설계  
> **수신 및 참조 대상**: `chapter-writer`, `fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`  
> **표준 용어 및 SoT 준수**: `docs/verified-facts.md` 기준 (산업안전보건법 제36조, 중대재해처벌법 제4조, 하인리히의 1:29:300 법칙, 제임스 리즌의 스위스 치즈 모델, 위험 통제 5단계 계층, 안전보건공단 KRAS 5×5 위험성 매트릭스, 오케스트레이션 하네스, 단계적 정보 공개, 우체국 안티패턴, 최소 권한 원칙, 컨텍스트 예산, 매개변수/인자, 메서드)

---

## 1. 핵심 갈등 구조: 전통적 서류 중심·사후 처방식 산업안전관리 vs 데이터·다중 에이전트 기반 스마트 안전관리 시스템

### 1.1 문제 상황(Pain Point): 형식적 위험성평가와 단일 서류 파이프라인의 붕괴
산업현장에서 중대재해가 반복되는 근본 원인은 안전 규정이 없어서가 아니라, 위험성평가와 작업허가(PTW, Permit to Work)가 **전통적 서류 중심·사후 처방식 행정 절차(Paper-based Reactive Safety)**로 전락했기 때문이다. 또한 이를 디지털화한다는 명목으로 현장의 모든 문서 작성·점검·승인을 단일 거대 LLM 에이전트(Monolithic Agent)나 1인 담당자에게 몰아넣을 경우 다음 세 가지 치명적인 구조적 실패가 발생한다.

1. **형식적 위험성평가(Copy-and-Paste Risk Assessment)와 문맥 중간 손실**:
   - 현장 여건(밀폐공간 용접, 화학물질 취급, 교대 작업)은 매일 바뀌는데도 전년도 위험성평가표를 그대로 복사해 서류철에만 보관한다. 단일 거대 에이전트에게 수백 페이지의 물질안전보건자료(MSDS), 작업환경측정 결과표, 법령 지침을 한꺼번에 입력해 위험성평가를 맡기면, LLM의 **문맥 중간 손실(Lost in the Middle)** 현상으로 인해 프롬프트 중간에 위치한 핵심 노출기준 수치나 안전 수칙을 망각하고 피상적인 일반론만 출력한다 [Lost in the Middle: How Language Models Use Long Contexts, Liu et al.](https://arxiv.org/abs/2307.03172) (2026-11-10 조회, TACL v2024).
2. **셀프 승인(Self-Approval)과 안전 무결성 훼손**:
   - 시공·생산 일정을 맞춰야 하는 작업 계획 작성자가 위험성평가와 안전 점검 승인까지 동시에 처리하면 **자기 확증 편향(Self-Confirmation Bias)**이 작동하여 치명적 유해·위험요인을 '허용 가능'으로 축소 판정한다. AI 파이프라인에서도 초고를 작성한 에이전트가 스스로 법령 검증과 코드 수정을 겸하면, 자신이 생성한 환각(Hallucination)이나 위험성 과소추정 오류를 합리화하여 그대로 통과시킨다 [Building Effective Agents, Anthropic Engineering](https://www.anthropic.com/research/building-effective-agents) (2026-11-10 조회, v2024.12).
3. **구두 보고 누락과 아차사고(Near-Miss) 휘발**:
   - 현장에서 발생한 사소한 가스 누출 징후나 아차사고가 카카오톡·무전기·구두 보고로만 전달되다 중간 관리자의 요약 과정에서 누락된다. 이는 다중 에이전트 시스템에서 중앙 리더가 모든 보고를 요약 중계하다 핵심 수치(예: 일산화탄소 농도)를 증발시키는 **우체국 안티패턴(Post-Office Anti-Pattern)**과 정확히 일치한다.

### 1.2 아키텍처 트레이드오프 및 비교 스펙

전통적 서류 중심 안전관리, 중앙 집중형 단일 AI 보조, 그리고 본 책이 설계하는 **데이터·P2P 다중 에이전트 기반 스마트 안전관리 하네스**의 공학적 트레이드오프를 비교하면 다음과 같다.

| 비교 차원 | 전통적 서류 중심·단일 에이전트 (Monolithic / Paper Safety) | 중앙 집중형 안전 중계 시스템 (Hub-and-Spoke Relay) | 데이터·P2P 다중 에이전트 스마트 안전 하네스 (본 아키텍처) |
| :--- | :--- | :--- | :--- |
| **아차사고 및 위험요인 기록 (System of Record)** | 구두 보고 후 휘발되거나 스캔 이미지·비정형 PDF로 방치됨 | 중앙 관리자에게 보고되나 요약 과정에서 현장 맥락 손실 | **아차사고 데이터 기록 시스템화** (`pdfplumber` 정형 파싱 + Git/DB 상태 영구 보존) |
| **위험작업 허가(PTW) 및 검증 권한 격리** | 작성자와 검토자 미분리로 **셀프 승인** 및 데이터 덮어쓰기 위험 상존 | 하위 역할은 분리되나 중앙 노드에 수정 권한 집중 | **최소 권한 원칙** 적용 (`Write`/`Edit` 허용 2인 vs `Read-Only` 독립 안전 검토 5인 분리) |
| **현장 수치 전달 및 통신 손실률** | 다단계 구두/서면 보고를 거치며 노출기준(TWA/STEL) 수치 왜곡 | **우체국 안티패턴** 발생 (리더가 요약 중계하며 정밀 수치 누락) | `SendMessage` 기반 **P2P 직접 소통**으로 원시 위험 데이터 및 행 번호 무손실 인계 |
| **위험성 결정 및 법규 검증 방식** | 담당자의 주관적 눈대중에 의존 (빈도×강도 계산 누락 빈발) | 프롬프트 권고에만 의존하여 확률적 계산 착오 발생 | KRAS 5×5 매트릭스($\text{빈도}\times\text{강도} \ge 8$) 및 법규 준수 여부를 파이썬 코드로 기계적 강제 |
| **한계점 및 대안 (Counter-arguments)** | 단일 소규모 작업이나 1회성 단순 질의에는 도입 비용이 가장 낮음 | 모든 통신을 단일 감사 노드에서 통제해야 하는 폐쇄망에서는 관리가 단순함 | 초기 데이터 파이프라인 및 7인 에이전트 하네스 구축 복잡도가 높고 데드락 방지 규약이 필수적임 |

> **핵심 반론 및 한계점(Trade-off 명시)**: 모든 소규모 영세 작업장이나 단순 1회성 안전 수칙 조회에 처음부터 7인 다중 에이전트 하네스를 가동하는 것은 과도한 엔지니어링(Over-engineering)이 될 수 있다 [Building Effective Agents, Anthropic Engineering](https://www.anthropic.com/research/building-effective-agents) (2026-11-10 조회, v2024.12). 그러나 화학물질 취급, 밀폐공간 작업, 다수 공정이 얽힌 중대재해 고위험 사업장이나 2,500~4,000 단어 규모의 엄밀한 산업안전 기술 문서·위험성평가서 컴파일 파이프라인에서는 단일 에이전트의 환각과 셀프 승인이 곧바로 인명 사고 및 법적 처벌로 직결되므로, 조율 오버헤드를 감수하고서라도 다중 방어선 하네스를 구축해야 한다.

---

## 2. 핵심 법령 및 안전공학적 이론 (1차 출처 기반)

본 장의 모든 안전 엔지니어링 설계와 파이썬 코드는 아래 5가지 대한민국 현행 법령 및 고전 안전공학 이론(1차 출처)에 엄격히 기반한다 (`docs/verified-facts.md` 단일 진실의 원천 일치).

### 2.1 산업안전보건법 제36조(위험성평가의 실시) 및 고용노동부 지침
- **법적 근거**: **산업안전보건법 제36조(위험성평가의 실시)**에 따라 사업주는 건설물, 기계·기구·설비, 원재료, 가스, 증기, 분진, 근로자의 작업행동 또는 그 밖의 업무로 인한 유해·위험요인을 찾아내어 부상 및 질병으로 이어질 수 있는 위험성의 크기가 허용 가능한 범위인지를 평가하여야 하고, 그 결과에 따라 조치를 하여야 하며, 근로자에게 교육 등 필요한 사항을 이행해야 한다 [국가법령정보센터 - 산업안전보건법 제36조](https://www.law.go.kr/) (2026-11-10 조회, 현행 법률).
- **표준 6단계 절차**: 고용노동부 고시『사업장 위험성평가에 관한 지침』은 위험성평가의 표준 절차를 다음 6단계로 규정한다 [고용노동부 - 사업장 위험성평가에 관한 지침](https://www.moel.go.kr/) (2026-11-10 조회, 고시 기준):
  1. **사전준비 (Preparation)**: 평가 대상 공정 선정, 안전보건정보(MSDS, 작업환경측정 결과, 재해사례) 수집
  2. **유해·위험요인 파악 (Hazard Identification)**: 작업장 순회점검, 아차사고 발굴, 체크리스트 등을 통해 유해·위험요인 도출
  3. **위험성 추정 (Risk Estimation)**: 파악된 유해·위험요인이 부상 또는 질병으로 이어질 가능성(빈도)과 중대성(강도)을 조합하여 위험성 크기 산출
  4. **위험성 결정 (Risk Determination)**: 추정된 위험성의 크기가 사업장에서 설정한 허용 가능 위험성 기준(예: KRAS 5×5 기준 8점 미만) 이하인지 판단
  5. **위험성 감소대책 수립 및 실행 (Risk Reduction Measures)**: 허용 불가능한 위험성에 대해 위험 통제 5단계 계층에 따라 감소대책을 수립·실행하고 잔여 위험성이 허용 가능 수준인지 재평가
  6. **기록 및 공유 (Documentation & Sharing)**: 평가 결과와 조치 내역을 기록·보존하고 전 근로자에게 공유

### 2.2 중대재해처벌법 제4조(사업주와 경영책임자등의 안전 및 보건 확보의무)
- **법적 근거**: **중대재해 처벌 등에 관한 법률(중대재해처벌법) 제4조**는 사업주 또는 경영책임자등이 실질적으로 지배·운영·관리하는 사업 또는 사업장에서 종사자의 안전·보건상 유해 또는 위험을 방지하기 위하여 재해예방에 필요한 인력 및 예산 등 **안전보건관리체계의 구축 및 그 이행에 관한 조치**를 다할 의무를 부과한다 [국가법령정보센터 - 중대재해 처벌 등에 관한 법률 제4조](https://www.law.go.kr/) (2026-11-10 조회, 현행 법률).
- **엔지니어링 시사점**: 동법 시행령 제4조 제3호는 유해·위험요인을 확인·개선하는 업무 절차를 마련하고 반기 1회 이상 이행 상황을 점검하도록 명시하며, 산업안전보건법 제36조에 따른 위험성평가를 실시하고 그 결과를 보고받은 경우 해당 절차를 이행한 것으로 본다. 단, 서류만 존재하고 실질적 위험 감소 조치나 이행 점검 기록(System of Record)이 없으면 법원에서 안전보건확보의무 이행으로 인정받지 못한다. 주의할 점으로, **위험성평가 조항은 산업안전보건법 제36조**이며 **안전보건확보의무가 중대재해처벌법 제4조**이므로 두 법 조항을 절대 혼동해서는 안 된다.

### 2.3 하인리히의 1:29:300 법칙(H. W. Heinrich, 1931)과 아차사고(Near-Miss) 데이터화
- **이론 원전**: 미국의 안전공학자 허버트 윌리엄 하인리히(H. W. Heinrich)가 1931년 저서 *Industrial Accident Prevention: A Scientific Approach*에서 보험사 재해 통계 75,000건을 분석하여 도출한 **하인리히의 1:29:300 법칙(Heinrich's Law)**에 따르면, 중상 또는 사망 재해 **1건**이 발생하기 전에 같은 원인으로 발생한 경미한 부상 사고 **29건**과 부상은 없었으나 아찔했던 잠재적 사고, 즉 **아차사고(Near-Miss) 300건**이 선행한다 [Industrial Accident Prevention, H. W. Heinrich / KOSHA 안전보건자료](https://www.kosha.or.kr/) (2026-11-10 조회, 1931 원전 기준). *(주의: 1:30:300이나 1:10:300으로 오기하는 것은 통계 수치 오류이므로 반드시 **1:29:300**으로 정확히 표기한다.)*
- **데이터 엔지니어링 시사점**: 중대재해(1건)는 발생 빈도가 낮아 사후 통계만으로는 예측이 불가능하지만, 수면 아래에 존재하는 300건의 아차사고와 작업환경 이상 징후를 정형 데이터(JSON/DB)로 포착하면 중대재해로 전이되기 전에 선제적으로 차단할 수 있다.

### 2.4 제임스 리즌의 스위스 치즈 모델(James Reason, 1990)과 위험 통제 5단계 계층(Hierarchy of Controls)
- **스위스 치즈 모델(Swiss Cheese Model)**: 영국의 심리학자 제임스 리즌(James Reason, 1990)이 *Human Error*에서 제시한 다중 방어선 이론으로, 산업 현장의 안전 방어선(설비적 방호장치, 표준안전작업절차(SOP), 위험작업허가제(PTW), 안전관리자 검토, 개인보호구(PPE))은 각각 완벽하지 않고 스위스 치즈처럼 잠재적 결함(구멍, Latent Conditions)과 능동적 실패(Active Failures)를 안고 있다. 여러 방어선의 구멍이 우연히 일직선으로 정렬(Alignment of Holes)될 때 비로소 위험 에너지가 모든 방어벽을 관통하여 중대재해가 발생한다 [Human Error, James Reason / KOSHA 안전공학 지침](https://www.kosha.or.kr/) (2026-11-10 조회, 1990 원전 기준).
- **위험 통제 5단계 계층(Hierarchy of Controls — NIOSH / ISO 45001)**: 위험성 감소대책을 수립할 때는 반드시 효과성과 근원적 차단력이 높은 순서대로 다음 **5단계 계층**을 우선 적용해야 한다 [안전보건공단 KOSHA / ISO 45001 위험 통제 계층](https://www.kosha.or.kr/) (2026-11-10 조회, 표준 지침):
  1. **1단계 제거 (Elimination)**: 유해·위험요인이나 위험 공정 자체를 물리적으로 없앰 (예: 고소작업을 지상 조립 공정으로 변경)
  2. **2단계 대체 (Substitution)**: 유해성이 높은 물질이나 설비를 덜 위험한 것으로 교체 (예: 유독성 유기용제를 수성 세척제로 대체)
  3. **3단계 공학적 대책 (Engineering Controls)**: 작업자와 유해위험요인을 물리적으로 격리하거나 환기·방호장치를 설치 (예: 국소배기장치 설치, 인터록 방호울 설치)
  4. **4단계 관리적 대책 (Administrative Controls)**: 작업 절차 변경, 작업 시간 단축, 안전표지 부착, 안전교육 및 작업허가제(PTW) 운영 (예: 밀폐공간 출입 시간 제한 및 감시인 배치)
  5. **5단계 개인보호구 (PPE, Personal Protective Equipment)**: 작업자에게 안전모, 안전대, 송기마스크, 화학복 등을 지급·착용하게 함
  - *(핵심 원칙: **제거·대체·공학적 대책을 우선 적용하고 개인보호구(PPE)는 최후의 보루로 적용**해야 한다. 개인보호구 지급만을 최우선 대책으로 삼는 위험성평가서는 안전공학 원칙 위반으로 기계적 반려 대상이다.)*

### 2.5 안전보건공단(KOSHA) KRAS 표준 5×5 위험성 매트릭스
- **산출 공식**: 안전보건공단(KOSHA)의 위험성평가 지원시스템(KRAS, Korea Risk Assessment System) 표준 모델에서 위험성(Risk)은 부상·질병이 발생할 **가능성(빈도, Likelihood/Frequency, 1~5점)**과 발생 시 예상되는 **중대성(강도, Severity, 1~5점)**의 곱으로 산출한다 [안전보건공단 KRAS 위험성평가 지원시스템 지침](https://www.kosha.or.kr/) (2026-11-10 조회, KRAS 표준 모델):
  $$\text{위험성(Risk)} = \text{가능성(빈도, 1\sim5)} \times \text{중대성(강도, 1\sim5)}$$
- **위험성 결정 기준**: 5×5 매트릭스(최소 1점 ~ 최대 25점)에서 산출된 점수가 **8점 이상**인 경우 **'허용 불가 위험(Unacceptable Risk)'**으로 분류하며, 작업을 즉시 중지하거나 위험 통제 5단계 계층에 따른 감소대책을 수립·실행하여 잔여 위험성을 8점 미만(허용 가능 범위)으로 낮춘 후에만 작업을 개시할 수 있다.

| 가능성(빈도) \ 중대성(강도) | **1 (경미: 아차사고/무상해)** | **2 (소: 응급처치/통원)** | **3 (중: 휴업재해)** | **4 (대: 중상해/장해)** | **5 (최대: 사망/중대재해)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **5 (매우 높음: 매일/빈번)** | 5 (보통) | **10 (높음·허용불가)** | **15 (매우높음·허용불가)** | **20 (매우높음·허용불가)** | **25 (매우높음·허용불가)** |
| **4 (높음: 주 1회/수시)** | 4 (낮음) | **8 (높음·허용불가)** | **12 (높음·허용불가)** | **16 (매우높음·허용불가)** | **20 (매우높음·허용불가)** |
| **3 (보통: 월/분기 1회)** | 3 (낮음) | 6 (보통) | **9 (높음·허용불가)** | **12 (높음·허용불가)** | **15 (매우높음·허용불가)** |
| **2 (낮음: 연 1회 이하)** | 2 (낮음) | 4 (낮음) | 6 (보통) | **8 (높음·허용불가)** | **10 (높음·허용불가)** |
| **1 (매우 낮음: 극히 희박)** | 1 (낮음) | 2 (낮음) | 3 (낮음) | 4 (낮음) | 5 (보통) |

---

## 3. 7인 안전 에이전트 오케스트레이션 하네스 적용

제임스 리즌의 **스위스 치즈 모델(다중 방어선)**과 보안 공학의 **최소 권한 원칙**을 결합하여, 본 프로젝트(`CLAUDE.md` 및 `docs/verified-facts.md`)는 산업안전 문서 및 위험성평가 파이프라인을 7인의 전문 에이전트로 구성된 **오케스트레이션 하네스(Orchestration Harness)**로 구동한다.

### 3.1 최소 권한 원칙(Principle of Least Privilege)과 셀프 승인 원천 차단
1975년 제롬 살처(Jerome Saltzer)와 마이클 슈뢰더(Michael Schroeder)가 정립한 **최소 권한 원칙** [The Protection of Information in Computer Systems, Saltzer & Schroeder](https://doi.org/10.1109/PROC.1975.9939) (2026-11-10 조회, Proceedings of the IEEE v63.9) 및 [NIST SP 800-53 Rev. 5, AC-6 Least Privilege](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) (2026-11-10 조회, v5.1.1)에 따라, 모든 에이전트는 본연의 안전 임무 수행에 필요한 최소한의 도구만 부여받는다.

프롬프트 지시문만으로 *"너는 안전 검토자이니 절대 위험성평가 원고를 직접 수정하지 마라"*고 부탁하면 LLM의 과도한 대리 행위(Excessive Agency) 성향으로 인해 검토 도중 원고를 임의로 덮어쓰는 사고가 발생한다 [OWASP Top 10 for Large Language Model Applications - LLM08: Excessive Agency](https://genai.owasp.org/llmrisk/llm08-excessive-agency/) (2026-11-10 조회, v2025.1). 따라서 에이전트 선언부(`.claude/agents/*.md`)의 `tools` 및 `disallowedTools` 설정을 통해 **위험작업 허가(PTW) 및 위험성평가 원고 작성자(`researcher`, `chapter-writer`)와 독립 안전 검토자 5인(`fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`)의 `Write`/`Edit` 권한을 런타임 수준에서 물리적으로 분리**하여 셀프 승인을 원천 차단한다 [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) (2026-11-10 조회, v1.0).

#### [표] 7인 안전 에이전트 역할·모델 라우팅·최소 권한 매트릭스 (`docs/verified-facts.md` SoT 일치)

| 에이전트명 (`.claude/agents/`) | 역할 구분 (산업안전 대응) | 모델 (`model`) | 허용 도구 (`tools`) | 차단 도구 (`disallowedTools`) | 설계 이유 (Why-First 및 Swiss Cheese 방어선) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`researcher`** | 작성 (안전법규·재해사례 조사) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Bash` | 1차 출처(산안법, KOSHA 지침)를 조사해 `research/`에 기록하되, 셸 실행으로 인한 로컬 환경 오염을 막기 위해 `Bash` 차단 |
| **`chapter-writer`** | 작성 (산업안전 원고 초고·개고) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `SendMessage` | `Bash`, `WebSearch`, `WebFetch` | 위험성평가 원고(`manuscripts/`)를 작성·수정하는 유일한 주체. 검증되지 않은 외부 블로그를 섞지 못하도록 웹 검색을 차단하고 리서치 노트만 참조하게 강제함 |
| **`fact-checker`** | 검토 (산안법·KOSHA 통계 검증) | `sonnet` | `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Write`, `Edit`, `Bash` | 제1방어선: 법 조항(제36조 vs 제4조) 및 통계(1:29:300) 대조를 위해 웹 접근은 허용하되, 원고 직접 수정(`Write`/`Edit`)은 박탈 |
| **`tech-reviewer`** | 검토 (안전 데이터·코드 검토) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 제2방어선: `pdfplumber` 파싱 및 KRAS 위험성 계산 코드의 정적 결함과 Hierarchy of Controls 준수 여부를 추론하되 읽기 전용으로 격리 |
| **`structure-reviewer`** | 검토 (구조·분량 2,500~4,000단어) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 제3방어선: 위험성평가 6단계 절차 누락 여부, 분량(2,500~4,000단어), 선행 지식 역전을 진단하는 읽기 전용 감시자 |
| **`proofreader`** | 검토 (산업안전 용어·AI 티 윤문) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 제4방어선: 산업안전 표준 용어(`glossary.md`) 및 번역투·이중피동을 검출하여 `chapter-writer`에게 수정을 요청함 |
| **`chapter-reviewer`** | 검토 (안전보건 총괄 비평·승인) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` | 제5방어선(최종 PTW 승인자): 직접 글을 고치는 순간 객관적 심판자 지위를 상실하므로 읽기 전용 상태에서 최종 `approved` 도장만 부여함 |

### 3.2 우체국 안티패턴(Post-Office Anti-Pattern) 타파와 P2P 직접 소통
- **문제 메커니즘**: 산업현장에서 현장 작업자가 발견한 치명적 유해·위험요인 수치(예: 밀폐공간 **일산화탄소(CO, CAS No. 630-08-0) 노출기준 TWA 30ppm, STEL 200ppm** 대비 실측치 45ppm 검출)가 반장 → 공사과장 → 안전팀장으로 구두 요약 보고되면서 *"환기 상태가 조금 안 좋다"*는 식으로 희석되는 현상이 바로 **우체국 안티패턴**이다 [Multi-Agent Collaboration Mechanisms: A Survey of LLMs, Tran et al.](https://arxiv.org/abs/2501.06322) (2026-11-10 조회, arXiv v2025.01).
- **해결책 (`SendMessage` P2P 직접 소통)**: 오케스트레이터는 제어 평면(팀 스폰, 모드 분기, 최종 종료)만 담당하고, 실제 안전 데이터와 검증 피드백이 오가는 데이터 평면은 에이전트 간 `SendMessage` 도구를 통한 P2P 직접 소통으로 처리한다.
  - `researcher`가 조사한 **일산화탄소 TWA 30ppm / STEL 200ppm** 수치와 `pdfplumber`의 `snap_tolerance: 3` 설정 사양은 오케스트레이터를 거치지 않고 `SendMessage`로 `chapter-writer`에게 무손실 직송된다.
  - `fact-checker`, `tech-reviewer`, `structure-reviewer` 3인 병렬 검증단 역시 발견한 결함의 정확한 행 번호(Line)와 수정 근거를 `chapter-writer`에게 직접 전송한다.

### 3.3 인지 부하 기반 모델 라우팅(`opus` 4인 vs `sonnet` 3인)과 3단계 단계적 정보 공개
1. **인지 부하(Cognitive Load) 기반 모델 라우팅**:
   - **고차원 안전 아키텍처 추론 및 집필 (`opus` 4인)**: `researcher`, `chapter-writer`, `tech-reviewer`, `chapter-reviewer`는 다중 법령·공학 이론 종합, 2,500~4,000 단어 서사 구성, 위험 통제 계층 아키텍처 검증을 수행하므로 최상위 추론 모델인 `opus`를 배치한다.
   - **규칙 기반 법령·수치 대조 및 교정 (`sonnet` 3인)**: `fact-checker`, `structure-reviewer`, `proofreader`는 `verified-facts.md` 1:1 대조, 단어 수 및 헤더 계층 점검, 금지 표현(denylist) 및 문체 교정을 수행하므로 빠르고 경제적인 `sonnet`을 배치한다. 이를 통해 검증 정확도를 100% 유지하면서 전체 리뷰 루프 토큰 비용을 **약 40~48% 절감**하고 병렬 검증 대기 시간을 단축한다 [FrugalGPT, Chen et al.](https://arxiv.org/abs/2305.05176) (2026-11-10 조회, arXiv v2023.05) 및 [Anthropic Model Overview & Pricing](https://docs.anthropic.com/en/docs/about-claude/models) (2026-11-10 조회, v2026.1).
2. **3단계 단계적 정보 공개(Progressive Disclosure)를 통한 컨텍스트 예산 보호**:
   - 제이콥 닐슨(Jakob Nielsen)의 **단계적 정보 공개** 원칙 [Progressive Disclosure, Jakob Nielsen / NNGroup](https://www.nngroup.com/articles/progressive-disclosure/) (2026-11-10 조회, v2006/2024) 및 [Claude Code Best Practices: Context Management](https://www.anthropic.com/engineering/claude-code-best-practices) (2026-11-10 조회, v2025.04)을 적용하여 **컨텍스트 예산(Context Budget)**을 공공재로 보호한다:
     - **Tier 1 (전역 헌법, ~800 토큰)**: `CLAUDE.md` 및 `.claude/agents/*.md` — 세션 시작 시 기본 로드 (최소 권한 가드레일 및 황금 워크플로 지도).
     - **Tier 2 (메타스킬 라우터, ~600 토큰)**: `.claude/skills/book-writer/SKILL.md` — 작업 명령 감지 시 7종 워크플로 중 해당 모드로 분기.
     - **Tier 3 (단일 워크플로 지연 로딩, ~1,200 토큰)**: `workflows/01-writing.md` 및 `docs/verified-facts.md` — 선택된 작업 모드의 단일 매뉴얼만 조건부 `Read`로 적재하고 나머지 6개 모드 매뉴얼(컴파일, 샘플링 감사 등)은 격리(0 토큰)하여, 컨텍스트 예산의 80% 이상을 실제 산업안전 법령·위험성평가 데이터 분석에 집중시킨다.

---

## 4. Why-First 코드 설계 스펙: 산업안전 PDF 테이블 추출 (`pdfplumber` v0.11.x vs `PyPDF2`/`pypdf`)

### 4.1 왜 산업안전 문서 파싱에서 `PyPDF2` 대신 `pdfplumber`를 써야 하는가? (Why-First)
에이전트 지시서에 이유(Why)를 설명하지 않고 *"무조건 `pdfplumber`만 써라"*고 강압적으로 지시하면, 에이전트는 단순 PDF 병합 작업에서도 `pdfplumber`의 존재하지 않는 쓰기 메서드를 환각으로 호출하는 **프롬프트 오버피팅(Overfitting)**에 빠진다 [Promptbreeder, Fernando et al.](https://arxiv.org/abs/2309.16797) (2026-11-10 조회, arXiv v2023.09).

산업안전 엔지니어링 파이프라인에서 **화학물질 물질안전보건자료(MSDS 16개 항목 중 '8. 노출방지 및 개인보호구' 표)**, **작업환경측정 결과표 PDF**, **KRAS 위험성평가표 PDF**를 파싱할 때 **`pdfplumber`(`v0.11.x`, `v0.11.4` 기준)**를 표준으로 채택하는 명확한 기술적 이유(Why)는 다음과 같다:
- 레거시 **`PyPDF2`(`v3.0.1` 이후 Deprecated)**나 그 후속작인 **`pypdf`(`v5.1.x`)**는 PDF 내부의 텍스트 스트림(Content Stream)만 순차적으로 읽어 들이므로, 표의 가로/세로 격자선과 셀 경계 정보가 완전히 소실된다.
- 만약 작업환경측정 결과표에 기재된 **일산화탄소(CAS No. `630-08-0`, TWA `30 ppm`, STEL `200 ppm`, 측정치 `45 ppm`)**와 **황화수소(CAS No. `7783-06-4`, TWA `1 ppm`, STEL `5 ppm`, 측정치 `0.5 ppm`)** 행이 줄글 텍스트로 뭉개지거나 열이 한 칸씩 밀려 파싱되면, 노출기준을 초과한 고위험 화학물질을 '정상'으로 오판하는 치명적인 안전 사고가 발생한다.
- 반면 **`pdfplumber`(`v0.11.4`)**는 `pdfminer.six` 엔진 위에서 개별 문자(`chars`), 선분(`lines`), 사각형(`rects`)의 정밀한 **$(x_0, top, x_1, bottom)$ 바운딩 박스 좌표(Bounding Box Coordinates)**를 1/72인치(pt) 단위로 계산하여, 표의 행/열 교차점과 병합 셀 구조를 2차원 배열(`List[List[Optional[str]]]`)로 완벽하게 복원한다 [pdfplumber GitHub Repository](https://github.com/jsvine/pdfplumber) (2026-11-10 조회, v0.11.4).

#### [표] 산업안전 PDF 파싱을 위한 Python 라이브러리 기술 스펙 비교

| 비교 항목 | `PyPDF2` (레거시) | `pypdf` (현대적 후속작) | `pdfplumber` (본 프로젝트 산업안전 표 추출 표준) |
| :--- | :--- | :--- | :--- |
| **최신 안정 버전 및 상태** | `v3.0.1` (2023년 이후 **Deprecated**, `pypdf`로 통합됨) [pypdf Documentation](https://pypdf.readthedocs.io/en/stable/) (2026-11-10 조회, v5.1.0) | `v5.1.x` (활발히 유지보수 중, 순수 Python) [pypdf Documentation](https://pypdf.readthedocs.io/en/stable/) (2026-11-10 조회, v5.1.0) | **`v0.11.x`** (`v0.11.4` 기준, `pdfminer.six` 기반) [pdfplumber GitHub Repository](https://github.com/jsvine/pdfplumber) (2026-11-10 조회, v0.11.4) |
| **내부 파싱 엔진 및 원리** | 단순 PDF 텍스트 스트림(Content Stream) 순차 추출 | 텍스트 스트림 추출 및 페이지 트리(Page Tree) 조작 | 개별 문자(Char), 선(Line), 사각형(Rect) 객체의 **정밀 $(x_0, top, x_1, bottom)$ 바운딩 박스 좌표** 계산 |
| **MSDS·작업환경측정 표 셀 구조 보존** | **불가능** — 화학물질명·CAS 번호·TWA/STEL 열 경계가 무너진 줄글로 뭉개짐 | **매우 제한적** — 좌표 기반 셀 구분이나 병합 셀(Merged Cell) 추출 API 없음 | **탁월함** — `extract_table()` 및 `table_settings`를 통해 격자선 교차점과 좌표를 분석해 2차원 리스트로 정확히 복원 |
| **시각적 디버깅 지원** | 미지원 | 미지원 | `Page.to_image()` 및 `debug_tablefinder()`로 인식된 셀 경계선을 시각적으로 렌더링하여 검증 가능 |
| **페이지 병합/분할/암호화** | 지원 (레거시 API) | **탁월함** (`PdfWriter`, `PdfMerger` 제공, 외부 C 의존성 없음) | **미지원** (읽기 및 레이아웃·좌표 분석 전용) |
| **권장 사용처 (Why-First 기준)** | 신규 안전 시스템 코드 작성 시 사용 금지 (`verified-facts.md` 규칙) | **경량 대안**: 안전교육 수료증 PDF 페이지 병합·분할, 메타데이터 조회 | **핵심 표준**: MSDS 16개 항목 표, 작업환경측정 결과표(TWA/STEL), KRAS 위험성평가표 등 **셀 구조 보존이 생명인 안전 데이터 추출** |

### 4.2 검증 가능한 표준 코드 스펙 (`pdfplumber` v0.11.4 + KRAS 위험성평가 자동 검증)
`chapter-writer`가 본문에 수록할 수 있도록, `pdfplumber`의 $(x_0, top, x_1, bottom)$ 좌표 기반 `table_settings` 매개변수 설정과 KRAS 5×5 매트릭스($\text{가능성}\times\text{중대성} \ge 8$) 및 위험 통제 5단계 계층 검증을 결합한 파이썬 레퍼런스 스펙을 제시한다.

```python
# 기준 환경: Python 3.11+, pdfplumber >= 0.11.0 (v0.11.4 기준)
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import pdfplumber


@dataclass(frozen=True)
class ChemicalHazardRecord:
    """작업환경측정 결과표 및 위험성평가표에서 추출한 정형 안전 데이터."""

    process_name: str
    chemical_name: str
    cas_number: str
    twa_limit_ppm: float
    stel_limit_ppm: float
    measured_ppm: float
    likelihood: int  # 가능성(빈도): 1 ~ 5
    severity: int  # 중대성(강도): 1 ~ 5
    proposed_control_tier: str  # '제거', '대체', '공학적 대책', '관리적 대책', '개인보호구(PPE)'

    @property
    def risk_score(self) -> int:
        """안전보건공단 KRAS 표준 모델에 따라 위험성(가능성 × 중대성)을 산출하는 메서드."""
        return self.likelihood * self.severity

    @property
    def is_unacceptable_risk(self) -> bool:
        """KRAS 5x5 매트릭스 기준 8점 이상이거나 노출기준(TWA) 초과 시 허용 불가 위험으로 판정한다."""
        return self.risk_score >= 8 or self.measured_ppm >= self.twa_limit_ppm


def extract_safety_table_with_pdfplumber(
    pdf_path: Path,
    page_index: int = 0,
) -> List[List[Optional[str]]]:
    """MSDS 또는 작업환경측정 결과표 PDF에서 셀 좌표(x0, top, x1, bottom)를 보존하여 표를 추출한다.

    단순 텍스트 스트림만 추출해 행/열 경계가 무너지는 레거시 PyPDF2(v3.0.1 Deprecated)와 달리,
    pdfplumber(v0.11.4)는 선분(lines)의 바운딩 박스 교차점을 계산하여 표 구조를 복원한다.
    """
    # table_settings 매개변수에 전달할 설정 딕셔너리 인자 정의
    table_settings: Dict[str, object] = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,          # 3pt 이내의 미세하게 어긋난 선분을 단일 셀 경계로 결합
        "intersection_tolerance": 3,  # 가로/세로 선분 교차점 허용 오차
    }

    with pdfplumber.open(pdf_path) as pdf:
        if page_index < 0 or page_index >= len(pdf.pages):
            raise IndexError(f"페이지 인덱스 범위 초과: 총 {len(pdf.pages)}페이지")

        page = pdf.pages[page_index]
        raw_table = page.extract_table(table_settings=table_settings)
        if not raw_table:
            return []

        return [
            [cell.replace("\n", " ").strip() if cell is not None else None for cell in row]
            for row in raw_table
        ]
```

---

## 5. `chapter-writer`를 위한 1장 집필 구성 가이드라인 (2,500~4,000 단어)

`docs/conventions.md` 및 `docs/verified-facts.md`의 품질 게이트를 한 번에 통과할 수 있도록 다음 6개 절 구조와 분량 배분을 권고한다.

1. **1.1절: 서류 중심 안전관리와 단일 에이전트의 붕괴 (~550 단어)**:
   - 형식적 위험성평가(전년도 복사·붙여넣기), 셀프 승인, 구두 보고 누락이 부르는 현장 참사를 제시하고, 이를 단일 거대 에이전트(Monolithic Agent)로 처리할 때 발생하는 문맥 중간 손실·자기 확증 편향·도구 과부하 문제를 비교표와 함께 서술한다.
2. **1.2절: 산업안전보건법 제36조·중대재해처벌법 제4조와 안전공학 3대 원리 (~700 단어)**:
   - 산업안전보건법 제36조(위험성평가 6단계 절차)와 중대재해처벌법 제4조(안전보건관리체계 구축)의 법적 연결고리를 해설한다. 이어 하인리히의 **1:29:300 법칙**(아차사고 데이터화), 제임스 리즌의 **스위스 치즈 모델**, **위험 통제 5단계 계층**(제거 → 대체 → 공학적 대책 → 관리적 대책 → 개인보호구(PPE)), 안전보건공단(KOSHA) **KRAS 5×5 위험성 매트릭스**(8점 이상 허용 불가 위험)를 정밀하게 정의한다.
3. **1.3절: 스위스 치즈 방어선으로서의 최소 권한 원칙과 7인 에이전트 하네스 (~650 단어)**:
   - 위험작업 허가(PTW) 및 위험성평가 원고 작성자(`researcher`, `chapter-writer`)와 독립 안전 검토자 5인(`fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`)의 `Write`/`Edit` 권한 분리 매트릭스를 표로 제시하고, 셀프 승인을 물리적으로 차단하는 메커니즘을 설명한다.
4. **1.4절: 우체국 안티패턴 타파와 인지 부하 기반 모델 라우팅·단계적 정보 공개 (~650 단어)**:
   - 현장 아차사고 및 유해인자 수치(일산화탄소 TWA 30ppm, STEL 200ppm)가 중간 요약 과정에서 증발하는 **우체국 안티패턴**을 `SendMessage` P2P 직접 소통으로 해결하는 과정을 Mermaid 시퀀스 다이어그램으로 시각화한다. 이어 `opus` 4인 vs `sonnet` 3인 모델 라우팅과 3단계 **단계적 정보 공개**(`CLAUDE.md` → `SKILL.md` → `workflows/*.md`)를 통한 **컨텍스트 예산** 최적화를 다룬다.
5. **1.5절: 스마트 안전 하네스 및 KRAS 위험성평가 검증 시뮬레이터 구현 (~550 단어)**:
   - 표준 라이브러리만으로 즉시 실행 가능한 파이썬 코드로 (1) 7인 안전 에이전트 최소 권한 가드레일, (2) P2P 아차사고/유해인자 무손실 전송, (3) KRAS 5×5 위험성 산출 및 위험 통제 5단계 계층 위반(PPE 최우선 적용 시도 차단) 자동 검증기를 구현한다.
6. **1.6절: Why-First 데이터 파싱 설계 — 왜 `PyPDF2` 대신 `pdfplumber`로 MSDS·작업환경측정 표를 추출하는가 (~550 단어)**:
   - 레거시 `PyPDF2`(`v3.0.1` Deprecated)/`pypdf`(`v5.1.x`)와 `pdfplumber`(`v0.11.4`)의 내부 파싱 원리($(x_0, top, x_1, bottom)$ 바운딩 박스 좌표 계산)를 비교표로 대조하고, 작업환경측정 결과표에서 일산화탄소 노출기준(TWA/STEL)과 위험성평가표를 추출하는 파이썬 실행 코드를 제시한다.

---

## 6. 참고문헌 및 1차 출처 목록 (Primary Sources)

1. [국가법령정보센터 - 산업안전보건법 제36조(위험성평가의 실시)](https://www.law.go.kr/) (2026-11-10 조회, 현행 법률) — 유해·위험요인 파악, 위험성 추정·결정 및 감소대책 조치 의무 규정.
2. [국가법령정보센터 - 중대재해 처벌 등에 관한 법률 제4조](https://www.law.go.kr/) (2026-11-10 조회, 현행 법률) — 사업주와 경영책임자등의 안전 및 보건 확보의무 및 안전보건관리체계 구축 규정.
3. [고용노동부 - 사업장 위험성평가에 관한 지침](https://www.moel.go.kr/) (2026-11-10 조회, 고용노동부고시) — 위험성평가 6단계 표준 절차(사전준비 → 유해·위험요인 파악 → 위험성 추정 → 위험성 결정 → 감소대책 수립·실행 → 기록 및 공유) 및 아차사고 반영 지침.
4. [안전보건공단(KOSHA) - KRAS 위험성평가 지원시스템 표준 모델 및 화학물질 노출기준](https://www.kosha.or.kr/) (2026-11-10 조회, KOSHA Guide) — 5×5 위험성 매트릭스($\text{가능성}\times\text{중대성}$, 8점 이상 허용 불가 위험), 위험 통제 5단계 계층(Hierarchy of Controls), 일산화탄소(TWA 30ppm, STEL 200ppm) 노출기준 명세.
5. **H. W. Heinrich**, *Industrial Accident Prevention: A Scientific Approach*, McGraw-Hill (1931) / [안전보건공단 재해예방 이론 해설](https://www.kosha.or.kr/) (2026-11-10 조회, v1931 원전) — 중상 1건 : 경상 29건 : 아차사고(Near-Miss) 300건의 **하인리히의 1:29:300 법칙** 정립.
6. **James Reason**, *Human Error*, Cambridge University Press (1990) / [안전보건공단 스위스 치즈 모델 지침](https://www.kosha.or.kr/) (2026-11-10 조회, v1990 원전) — 다중 방어선(설비 방호, SOP, PTW, PPE)의 결함 정렬로 인한 중대재해 발생 메커니즘 규명.
7. [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) (2026-11-10 조회, v1.0) — 에이전트별 `tools`, `disallowedTools`, `model` 선언 및 컨텍스트 격리 명세.
8. [Building Effective Agents, Anthropic Engineering](https://www.anthropic.com/research/building-effective-agents) (2026-11-10 조회, v2024.12) — 단일 에이전트 대비 다중 에이전트 오케스트레이션 하네스의 트레이드오프 및 검증 분리 원칙.
9. [Claude Code Best Practices: Context Management](https://www.anthropic.com/engineering/claude-code-best-practices) (2026-11-10 조회, v2025.04) — 컨텍스트 예산 관리 및 계층적 지침 로드 패턴.
10. [Lost in the Middle: How Language Models Use Long Contexts, Liu et al.](https://arxiv.org/abs/2307.03172) (2026-11-10 조회, TACL v2024) — 장문 컨텍스트 윈도우 중간 영역의 안전 수칙·제약 조건 망각 현상 실증 논문.
11. [The Protection of Information in Computer Systems, Saltzer & Schroeder](https://doi.org/10.1109/PROC.1975.9939) (2026-11-10 조회, Proceedings of the IEEE v63.9) — 최소 권한 원칙(Principle of Least Privilege) 원전 논문.
12. [NIST SP 800-53 Rev. 5, AC-6 Least Privilege](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) (2026-11-10 조회, v5.1.1) — 작성자와 검토자의 권한 분리 보안 표준.
13. [OWASP Top 10 for Large Language Model Applications - LLM08: Excessive Agency](https://genai.owasp.org/llmrisk/llm08-excessive-agency/) (2026-11-10 조회, v2025.1) — LLM의 과도한 대리 행위 위험 및 런타임 가드레일 권고안.
14. [Multi-Agent Collaboration Mechanisms: A Survey of LLMs, Tran et al.](https://arxiv.org/abs/2501.06322) (2026-11-10 조회, arXiv v2025.01) — 중앙 집중 중계(우체국 안티패턴)의 정보 손실과 P2P 직접 소통 비교 연구.
15. [Progressive Disclosure, Jakob Nielsen / NNGroup](https://www.nngroup.com/articles/progressive-disclosure/) (2026-11-10 조회, v2006/2024) — 단계적 정보 공개를 통한 인지 과부하 방지 원리.
16. [pdfplumber GitHub Repository & Documentation](https://github.com/jsvine/pdfplumber) (2026-11-10 조회, v0.11.4) — $(x_0, top, x_1, bottom)$ 바운딩 박스 좌표 기반 PDF 테이블 추출 및 `table_settings` API 명세.
17. [pypdf Official Documentation](https://pypdf.readthedocs.io/en/stable/) (2026-11-10 조회, v5.1.0) — `PyPDF2`(`v3.0.1` Deprecated)의 통합 경위 및 텍스트 스트림 추출 한계 명세.

---

## 7. 제출 전 자기 점검 체크리스트 (Self-Verification)

- [x] **메타데이터 주석 포함**: 리서치 문서 최상단에 `<!-- chapter: 01, target_version: 1.0, status: verified -->` 형식의 메타데이터 주석이 포함되었는가?
- [x] **1차 출처 비율 및 사실 레지스트리(`verified-facts.md`) 일치**: 산업안전보건법 제36조, 중대재해처벌법 제4조, 하인리히의 1:29:300 법칙, 제임스 리즌의 스위스 치즈 모델, 위험 통제 5단계 계층, 안전보건공단 KRAS 5×5 매트릭스(8점 이상 허용 불가), 7인 에이전트 권한 매트릭스가 1차 출처 및 `docs/verified-facts.md`와 100% 일치하는가?
- [x] **트레이드오프 및 갈등 구조 명시**: 전통적 서류 중심·사후 처방식 안전관리(형식적 위험성평가, 셀프 승인, 구두 보고 누락) vs 데이터·다중 에이전트 기반 스마트 안전관리 시스템의 갈등 구조와 한계점, 그리고 `PyPDF2`/`pypdf` vs `pdfplumber`(`v0.11.4`)의 기술적 트레이드오프가 마크다운 비교표로 명확히 정리되었는가?
- [x] **직접 인계 및 브리핑 완료**: 오케스트레이터 및 후속 파이프라인이 즉시 참조할 수 있도록 파일 경로와 핵심 브리핑이 준비되었는가?
