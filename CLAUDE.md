# CLAUDE.md - 책 집필을 위한 7인 다중 에이전트 오케스트레이션 하네스

이 프로젝트는 독립적인 역할을 수행하는 7개의 AI 에이전트가 협업하여 단행본을 집필·검토·교정·출판하는 **오케스트레이션 하네스(Orchestration Harness)**입니다.

## 1. 디렉터리 구조 (3-Tier Progressive Disclosure)

```text
.
├── .claude/
│   ├── agents/                         # 1단계: 7인의 전문 에이전트 정의 (최소 권한 및 모델 라우팅)
│   │   ├── researcher.md               # [Opus / Write] 자료 조사 및 1차 출처 검증
│   │   ├── chapter-writer.md           # [Opus / Write] 초고 작성 및 리뷰 피드백 반영
│   │   ├── fact-checker.md             # [Sonnet / Read-Only] 사실 관계 및 통계/인용 검증
│   │   ├── tech-reviewer.md            # [Opus / Read-Only] 코드 실행 가능성 및 아키텍처 심층 검토
│   │   ├── structure-reviewer.md       # [Sonnet / Read-Only] 논리 구조 및 분량(2,500~4,000 단어) 검토
│   │   ├── proofreader.md              # [Sonnet / Read-Only] 맞춤법, 번역투 교정, 용어 통일
│   │   └── chapter-reviewer.md         # [Opus / Read-Only] 독자 관점 총괄 비평 및 최종 승인
│   └── skills/
│       └── book-writer/                # 2단계: 오케스트레이터 메타스킬
│           ├── SKILL.md                # 30+ 트리거 키워드 및 7종 작업 모드 라우팅 테이블
│           ├── workflows/              # 3단계: 조건부 지연 로딩(Lazy Loading) 세부 워크플로
│           │   ├── 01-writing.md
│           │   ├── 02-revision.md
│           │   ├── 03-compile.md
│           │   ├── 04-sampling-review.md
│           │   ├── 05-consolidation.md
│           │   ├── 06-supervised-review.md
│           │   └── 07-paragraph-walkthrough.md
│           └── references/             # 공통 품질 기준 및 Why-First 지시서
│               ├── style-guide.md
│               ├── quality-checklist.md
│               └── glossary.md
└── book-writer/                        # 루트 레벨 미러 패키지 (동일 구조 제공)
```

## 2. 핵심 아키텍처 가드레일

1. **작성(Write)과 검토(Review)의 권한 분리**:
   - 직접 파일을 생성·수정하는 `researcher`, `chapter-writer`에게만 `Read`, `Write`, `Edit` 도구를 부여합니다.
   - 검토자인 `fact-checker`, `tech-reviewer`, `structure-reviewer`, `proofreader`, `chapter-reviewer`는 `disallowedTools: [Write, Edit, Bash]`를 명시하여 원고 훼손을 원천 방지합니다.
2. **비용과 성능을 고려한 모델 라우팅**:
   - 장문 생성 및 고차원 추론이 필요한 `researcher`, `chapter-writer`, `tech-reviewer`, `chapter-reviewer`에는 **`opus`** 모델을 할당합니다.
   - 규칙 적용 및 범위가 명확한 대조 작업인 `fact-checker`, `structure-reviewer`, `proofreader`에는 **`sonnet`** 모델을 배치합니다.
3. **우체국 안티패턴 방지 (`SendMessage` 직접 소통)**:
   - 오케스트레이터(`book-writer/SKILL.md`)는 팀 구성/해체와 모드 라우팅만 담당하고, 실행 중 사회/갈등 구조, 기술 트레이드오프, 검토 피드백은 에이전트들이 `SendMessage`로 직접 주고받습니다.
4. **제출 전 3대 자기 점검 및 Why-First 원칙**:
   - 모든 챕터는 `메타데이터 주석 포함`, `분량 2,500~4,000 단어`, `코드 블록 실행 가능` 여부를 검증해야 하며, 모든 지시서와 설명은 이유(Why)를 먼저 제시하여 오버피팅을 방지합니다.
