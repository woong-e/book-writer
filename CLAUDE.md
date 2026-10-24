# CLAUDE.md — 에이전트 진입점 (Agent Entry Point & Map)

> **이 레포는 책 한 권을 집필·출판하는 다중 에이전트 오케스트레이션 하네스(Orchestration Harness)다.** 코드가 아니라 원고가 최종 산출물이다.
> OpenAI의 *Harness Engineering* 원문(Ryan Lopopolo, 2026-02-11)에서 **도출한 8원칙**과 **7인 다중 에이전트 협업 파이프라인(`book-writer`)**을 결합하여, 에이전트가 안정적으로 한 장씩 조사·집필·검증·교정·출판하도록 설계되었다.
> 핵심 철학: **"사람이 조종하고, 에이전트가 실행한다" (Humans steer, agents execute — 원칙 1)**.
> 새 세션은 이 파일(약 100줄의 지도)부터 읽고, 작업 모드에 따라 아래 "지도"의 해당 문서로 조건부 점프(Progressive Disclosure)한다.

## 1. 지금 어디까지 했나 (관측성 · 원칙 3·4)

```bash
python scripts/status.py          # 장별 상태(skeleton/draft/revised/proofread/reviewed/approved/published) + 진척률
python scripts/verify.py          # 원고 규약·사실(denylist)·분량(2,500~4,000단어)·코드·게이트 도장 기계적 검증
```

진행 상태는 **각 원고(`manuscripts/<slug>.md`)의 front-matter 및 상단 메타데이터 주석에만** 저장된다(머릿속·외부 메모 금지). 세션이 끊겨도 위 두 명령으로 즉시 복원된다(원칙 3: 프로젝트 저장소 지식을 기록 시스템으로 삼아라).

## 2. 지도 (필요할 때만 점프 — 단계적 정보 공개)

| 알고 싶은 것 | 문서 경로 (Single Source of Truth) |
| :--- | :--- |
| 책 구조(부/장/슬러그/공식 링크)의 단일 원천 | [`docs/toc.json`](docs/toc.json) ← 구조 변경은 **여기 먼저** 고치고 `scripts/scaffold.py` 실행 |
| 8원칙 정의·출처·명칭·금지 표현(denylist) | [`docs/verified-facts.md`](docs/verified-facts.md) (사실 SoT) |
| 톤·용어·장 템플릿·front-matter·메타데이터 규격 | [`docs/conventions.md`](docs/conventions.md) |
| 7인 에이전트 역할·모델 라우팅·최소 권한 정의 | [`.claude/agents/`](.claude/agents/) (`researcher`, `chapter-writer`, `fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`) |
| 오케스트레이터 메타스킬 (7종 작업 모드 라우팅) | [`.claude/skills/book-writer/SKILL.md`](.claude/skills/book-writer/SKILL.md) (미러: [`book-writer/SKILL.md`](book-writer/SKILL.md)) |
| 모드별 지연 로딩(Lazy Loading) 워크플로 7종 | [`.claude/skills/book-writer/workflows/`](.claude/skills/book-writer/workflows/) (`01-writing.md` ~ `07-paragraph-walkthrough.md`) |
| Why-First 지시서·품질 체크리스트·한국어 AI 티 제거 | [`.claude/skills/book-writer/references/`](.claude/skills/book-writer/references/) (`style-guide.md`, `quality-checklist.md`, `glossary.md`, `ai-tell-taxonomy.md`) |
| 리서치 노트 및 실제 원고 | [`research/`](research/), [`manuscripts/`](manuscripts/) |

## 3. 골든 워크플로우 (7인 에이전트 + 기계적 검증 게이트)

```text
docs/toc.json (구조 SoT)
 └─ scripts/scaffold.py ─▶ manuscripts/*.md 골격(skeleton) 결정론적 생성 (멱등)
      └─ [1. 자료 조사] researcher (Opus / Write) ─▶ research/<slug>-notes.md 작성 후 SendMessage 직접 브리핑
           └─ [2. 초고 작성] chapter-writer (Opus / Write) ─▶ status: draft (2,500~4,000단어, 실행 가능 코드, 메타데이터 주석)
                └─ [3. 3인 병렬 검증 (Read-Only)] ─▶ SendMessage P2P 피드백 루프
                │    ├─ 3a. fact-checker (Sonnet)      + scripts/crosscheck.py (verified-facts.md 대조 → crosscheck: pass)
                │    ├─ 3b. tech-reviewer (Opus)       (코드 실행 가능성·Why-First 아키텍처 검증)
                │    └─ 3c. structure-reviewer (Sonnet) (분량 2,500~4,000단어·섹션 구조·선행 지식 역전 검증)
                └─ [4. 교정·윤문] proofreader (Sonnet / Read-Only) ─▶ 10대 AI 티(번역투·이중피동) 제거 & 용어 통일 (humanized: pass)
                     └─ [5. 총괄 비평 & 기계 검증] chapter-reviewer (Opus / Read-Only) + scripts/verify.py ─▶ status: approved
```

## 4. 절대 규칙 (위반은 버그 — `scripts/verify.py`가 기계적으로 차단)

1. **작성(Write)과 검토(Review)의 최소 권한 분리**: 직접 파일을 수정하는 `researcher`, `chapter-writer`에게만 `Read`, `Write`, `Edit`을 부여한다. 검토 역할 5인(`fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`)은 `disallowedTools: [Write, Edit, Bash]`로 본문 직접 수정을 원천 차단한다.
2. **비용과 성능을 고려한 모델 라우팅**: 장문 생성과 고차원 추론이 필요한 역할(`researcher`, `chapter-writer`, `tech-reviewer`, `chapter-reviewer`)에는 **`opus`**를, 규칙 적용·사실 대조·교정 작업(`fact-checker`, `structure-reviewer`, `proofreader`)에는 **`sonnet`**을 배치한다.
3. **우체국 안티패턴(Post-Office Anti-Pattern) 금지**: 오케스트레이터는 팀 구성(Spawn)·모드 분기·해체(Teardown)만 맡고, 실행 중 사회/갈등 구조, 기술 트레이드오프, 수정 피드백은 에이전트들이 `SendMessage`로 직접 소통한다.
4. **제출 전 3대 자기 점검 & 강제 게이트**:
   - 상단 **메타데이터 주석**(`<!-- chapter: ... -->`) 및 YAML front-matter 필수 포함
   - 챕터 본문 분량 **2,500~4,000 단어(어절)** 엄수
   - 모든 **코드 블록 실행 가능** 및 **Why-First 원칙**(예: 단순 텍스트 스트림만 추출하는 `PyPDF2` 대신 셀 좌표와 레이아웃 구조를 보존하는 `pdfplumber` 사용 이유 명시) 적용
   - `crosscheck: pass` 및 `humanized: pass` 도장 없이는 `reviewed`/`approved`/`published` 승격 불가 (`verify.py`가 차단).
