"""하네스 공통 헬퍼 — 표준 라이브러리(stdlib)만 사용 (외부 의존성 zero).

Why-First 설계 이유:
외부 패키지(PyYAML 등)에 의존하면 에이전트나 CI 환경마다 가상환경 차이로 인해
검증 스크립트 자체가 깨지는 부작용이 발생한다. 따라서 이 프로젝트가 사용하는
상단 HTML 메타데이터 주석(`<!-- chapter: ... -->`)과 YAML front-matter 부분집합을
순수 표준 라이브러리로 파싱·갱신하여 결정론적 실행(원칙 5·ch14)을 보장한다.
"""
from __future__ import annotations
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUSCRIPT_DIR = os.path.join(ROOT, "manuscripts")
TOC_PATH = os.path.join(ROOT, "docs", "toc.json")
FACTS_PATH = os.path.join(ROOT, "docs", "verified-facts.md")


def load_toc() -> dict:
    with open(TOC_PATH, encoding="utf-8") as f:
        return json.load(f)


def iter_toc_chapters(toc: dict):
    """(part_dict, chapter_dict) 튜플을 toc.json 순서대로 산출."""
    for part in toc.get("parts", []):
        for ch in part.get("chapters", []):
            yield part, ch


def _coerce(value: str):
    v = value.strip()
    if v in ("null", "~", ""):
        return None
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def parse_metadata_comment(text: str) -> dict:
    """최상단 HTML 메타데이터 주석 `<!-- key: val, ... -->`을 파싱하여 dict로 반환."""
    m = re.match(r"^\s*<!--(.*?)-->", text, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1).strip()
    result = {}
    # chapter: 01, title: "...", word_count: 3445, status: approved 등 추출
    for k in ("chapter", "title", "word_count", "status", "author"):
        km = re.search(rf"\b{k}\s*:\s*(\"[^\"]*\"|[^,\n\]]+)", raw)
        if km:
            result[k] = _coerce(km.group(1))
    return result


def parse_front_matter(text: str) -> tuple[dict, str]:
    """마크다운 텍스트에서 (front_matter_dict, body) 반환.
    최상단에 HTML 메타데이터 주석이 있는 경우 이를 건너뛰고 YAML front-matter를 파싱하며,
    YAML front-matter가 없으면 HTML 주석 메타데이터를 폴백으로 결합한다.
    """
    meta_comment = parse_metadata_comment(text)
    stripped = re.sub(r"^\s*<!--.*?-->\s*\n?", "", text, count=1, flags=re.DOTALL)

    if not stripped.startswith("---"):
        return meta_comment, stripped

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", stripped, re.DOTALL)
    if not m:
        return meta_comment, stripped

    block, body = m.group(1), m.group(2)
    data = dict(meta_comment)
    current_list_key = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        list_item = re.match(r"^\s+-\s+(.*)$", raw)
        if list_item and current_list_key is not None:
            data[current_list_key].append(_coerce(list_item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2)
        if val.strip() in ("", "[]"):
            data[key] = []
            current_list_key = key if val.strip() == "" else None
        else:
            data[key] = _coerce(val)
            current_list_key = None
    return data, body


def set_front_matter_key(text: str, key: str, value) -> str:
    """YAML front-matter 블록에서 `key:` 스칼라를 value로 교체(없으면 닫는 --- 앞에 삽입).
    최상단 HTML 주석과 본문은 그대로 보존한다.
    """
    val_str = "null" if value is None else (f'"{value}"' if isinstance(value, str) else str(value))
    prefix = ""
    rest = text
    cm = re.match(r"^(\s*<!--.*?-->\s*\n)", text, re.DOTALL)
    if cm:
        prefix = cm.group(1)
        rest = text[len(prefix):]

    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n?)(.*)$", rest, re.DOTALL)
    if not m:
        raise ValueError("YAML front-matter 블록이 없습니다.")
    head, block, close, body = m.groups()
    line = f"{key}: {val_str}"
    if re.search(rf"^{re.escape(key)}:.*$", block, re.MULTILINE):
        block = re.sub(rf"^{re.escape(key)}:.*$", line, block, count=1, flags=re.MULTILINE)
    else:
        block = block + "\n" + line
    return prefix + head + block + close + body


def count_words(body: str) -> int:
    """코드 블록(```...```)과 마크다운 표 구분선(| :--- |)을 제외한 순수 본문 산문의 단어(어절) 수를 계산한다."""
    no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    # 마크다운 표 기호(|) 및 구분선(---) 토큰 제외
    no_table_pipes = re.sub(r"[|:-\u2500-\u257f]{2,}", " ", no_code)
    return len(re.findall(r"[가-힣A-Za-z0-9_]+[^\s|]*", no_table_pipes))


def chapter_path(slug: str) -> str:
    return os.path.join(MANUSCRIPT_DIR, f"{slug}.md")


def iter_manuscript_files():
    if not os.path.isdir(MANUSCRIPT_DIR):
        return
    for name in sorted(os.listdir(MANUSCRIPT_DIR)):
        if name.endswith(".md") and not name.startswith("_"):
            path = os.path.join(MANUSCRIPT_DIR, name)
            with open(path, encoding="utf-8") as f:
                yield path, f.read()
