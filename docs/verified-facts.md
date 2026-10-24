# 검증된 핵심 사실 레지스트리 (Single Source of Truth)

> 이 책 전체에서 반복 등장하는 **출처·명칭·하네스 엔지니어링 8원칙·7인 에이전트 아키텍처 정의**의 진실의 원천(SoT)이다.
> 모든 장은 이 표와 일치해야 한다. 불일치는 버그다 → `fact-checker` 에이전트 및 `scripts/verify.py`, `scripts/crosscheck.py`가 자동 검출한다.
> 사실이 바뀌면 **여기를 먼저 고치고**, 그 다음 본문을 고친다.
> 마지막 검증일: 2026-10-24

---

## 1. 출처·명칭 사실 표

| key | 값 | 근거 / 비고 |
| :--- | :--- | :--- |
| `harness_eng_name` | **Harness Engineering** (한국어: 하네스 엔지니어링) | 원문 제목 "Harness engineering: leveraging Codex in an agent-first world" |
| `harness_eng_author` | **OpenAI** (Ryan Lopopolo, Member of Technical Staff) | OpenAI 팀의 사내 실험 보고. 저자 표기는 Ryan Lopopolo |
| `harness_eng_source` | `https://openai.com/index/harness-engineering/` | 원문(canonical) 출처. 발행일 2026-02-11 |
| `harness_eng_philosophy` | **"사람이 조종하고, 에이전트가 실행한다"** (Humans steer, agents execute) | 원문의 핵심 한 줄. 모든 원칙과 오케스트레이션의 뿌리 |
| `harness_eng_experiment` | 빈 git 리포(2025-08 말 첫 커밋)에서 5개월간 **약 100만 줄**을 **Codex 에이전트만으로**(사람 손코딩 0줄) 구축. 수동 대비 **약 1/10 시간** 추정 | 엔지니어 3→7명, 약 1,500 PR, 내부 베타 출시·실사용 |
| `entropy_friday_cleanup` | 초기엔 **매주 금요일(엔지니어링 시간의 약 20%)**을 "AI 슬로프" 수동 정리에 썼으나 생성 속도를 못 따라가, **"황금 원칙(Golden Principles)" + 반복 Codex 정리 태스크**(doc-gardening)로 전환 | 원문 "Entropy and garbage collection" 절 (원칙 8 근거) |
| `principle_count` | **8개** (이 책이 원문 11개 절 중 8개 절을 한 원칙씩 선별·도출) | ⚠️ 원문은 원칙을 번호로 명시하지 않는다. "원문이 정한 8원칙" 단정 금지 → **"원문에서 도출한 8원칙"**으로 표기 |
| `ralph_wiggum_loop` | 에이전트 검토자가 모두 만족할 때까지 반복하는 자율 피드백 루프 | 원문이 자기 PR 완성 과정을 "사실상 Ralph Wiggum Loop"라 부름 |
| `claude_code_docs_domain` | `code.claude.com/docs` | 구 도메인(`docs.claude.com/docs`) 표기 금지 |
| `pdf_table_extraction_rule` | PDF 테이블 추출에는 **`pdfplumber`**(`v0.11.x`)를 사용한다 | `PyPDF2`(`v3.0.1` 이후 Deprecated)는 단순 텍스트 스트림 추출에 특화되어 표의 셀 좌표와 레이아웃 구조를 보존하지 못하기 때문 (Why-First 원칙의 대표 예시) |

---

## 2. 하네스 엔지니어링 8원칙 (원문에서 도출 — 전 장 통일)

> ⚠️ **원문에 없는 카운트 주의**: OpenAI 원문 본문은 **11개 절**로 구성되며, 그중 **원칙을 담은 8개 절을 한 원칙씩 선별·도출**했다(실험 도입부, "What 'agent-generated' actually means" 개념 절, 맺음 절 등 3개 절은 원칙 미승격). 따라서 "원문이 정한 8원칙"이나 "한 절당 한 원칙으로 도출(1:1 전수 매핑)"이라고 단정하면 `verify.py`가 FAIL시킨다.

| # | 영문 (도출 명칭) | 한국어 표준어 | 원문 절 (근거, verbatim) |
| :--- | :--- | :--- | :--- |
| 1 | Humans steer, agents execute | **사람이 조종하고, 에이전트가 실행한다** | Redefining the role of the engineer |
| 2 | Make the application legible to agents | **애플리케이션을 에이전트가 읽게 하라** | Increasing application legibility |
| 3 | Repository knowledge as a system of record | **프로젝트 저장소 지식을 기록 시스템으로 삼아라** | We made repository knowledge the system of record |
| 4 | Optimize for agent legibility | **에이전트 가독성에 최적화하라** | Agent legibility is the goal |
| 5 | Enforce architecture and taste mechanically | **아키텍처와 취향을 기계적으로 강제하라** | Enforcing architecture and taste |
| 6 | Let throughput reshape merge philosophy | **처리량에 맞춰 병합 철학을 바꿔라** | Throughput changes the merge philosophy |
| 7 | Encode the autonomy loop | **자율 루프를 시스템으로 구축하라** | Increasing levels of autonomy |
| 8 | Garbage-collect entropy | **엔트로피를 가비지 컬렉션하라** | Entropy and garbage collection |

---

## 3. 7인 에이전트 역할·모델 라우팅·최소 권한 매트릭스 (SoT)

| 에이전트명 (`.claude/agents/`) | 역할 구분 | 모델 (`model`) | 허용 도구 (`tools`) | 차단 도구 (`disallowedTools`) |
| :--- | :--- | :--- | :--- | :--- |
| **`researcher`** | 작성 (자료 조사) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Bash` |
| **`chapter-writer`** | 작성 (초고·개고) | `opus` | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `SendMessage` | `Bash`, `WebSearch`, `WebFetch` |
| **`fact-checker`** | 검토 (사실 확인) | `sonnet` | `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `SendMessage` | `Write`, `Edit`, `Bash` |
| **`tech-reviewer`** | 검토 (기술·코드) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`structure-reviewer`** | 검토 (구조·분량) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`proofreader`** | 검토 (교정·윤문) | `sonnet` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |
| **`chapter-reviewer`** | 검토 (총괄 비평) | `opus` | `Read`, `Grep`, `Glob`, `SendMessage` | `Write`, `Edit`, `Bash`, `WebSearch`, `WebFetch` |

---

## 4. 금지 표현 (denylist) — `scripts/verify.py` 기계적 차단

| 금지 패턴 | 이유 | 올바른 표현 |
| :--- | :--- | :--- |
| `OpenAI의 8원칙`, `OpenAI가 정의한 8원칙`, `원문의 8원칙` | 원문은 원칙을 번호로 명시하지 않음 | "원문에서 도출한 8원칙" / "이 책의 8원칙" |
| `한 절당 한 원칙으로 도출` | 원문 11개 절 중 8개만 원칙으로 선별·도출함 | "8개 절을 한 원칙씩 선별·도출" |
| `12-Factor Agents`, `HumanLayer`, `Dexter Horthy` | 폐기된 구 주제·구 출처 | 하네스 엔지니어링(Harness Engineering) / OpenAI(Ryan Lopopolo) |
| `docs.claude.com/docs` | 구 도메인 | `code.claude.com/docs` |
| `정본` | 독자 대상 용어 통일 규칙 | `원문` |
