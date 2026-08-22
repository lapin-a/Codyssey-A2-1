import json
import sys

REQUIRED_FIELDS = ["topic"]


def load_brief(path):
    """브리프 JSON 파일을 읽고 검증한 뒤, 내부 로직에서 쓰기 좋은 형태로 정규화해서 반환한다."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"[에러] 브리프 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[에러] 브리프 JSON 형식이 올바르지 않습니다: {e}")
        sys.exit(1)

    _validate_brief(raw)
    return _normalize_brief(raw)


def _validate_brief(raw):
    missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
    if missing:
        print(f"[에러] 브리프에 필수 필드가 없습니다: {', '.join(missing)}")
        sys.exit(1)


def _normalize_brief(raw):
    """topic만 필수, 나머지는 선택. output_requirement의 세부 옵션에는 기본값을 채운다."""
    output_req = raw.get("output_requirement", {}) or {}
    color_req = output_req.get("color_palette", {}) or {}

    return {
        "topic": raw["topic"],
        "target": raw.get("target", ""),
        "keywords": raw.get("keywords", []),
        "tone": raw.get("tone", ""),
        "naming_count": output_req.get("naming_count", 4),
        "slogan_count": output_req.get("slogan_count", 3),
        "story_length": output_req.get("story_length", 300),
        "main_colors": color_req.get("main_colors", 1),
        "sub_colors": color_req.get("sub_colors", 3),
        "logo_concepts_count": output_req.get("logo_concepts_count", 3),
    }
