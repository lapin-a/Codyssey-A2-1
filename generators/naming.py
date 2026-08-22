from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.6-luna"


def load_brief(path: str | Path) -> dict[str, Any]:
    """JSON 브리프를 읽습니다.

    brief.json에 // 설명 주석이 들어간 경우도 처리할 수 있도록
    줄 끝 주석을 제거합니다. 엄격한 JSON만 사용한다면 json.loads만
    사용해도 됩니다.
    """
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"(^|\s)//.*$", r"\1", text, flags=re.MULTILINE)

    try:
        brief = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"브리프 JSON 형식이 올바르지 않습니다: {exc}") from exc

    if not isinstance(brief, dict):
        raise ValueError("브리프의 최상위 구조는 JSON 객체여야 합니다.")
    return brief


def get_schema(brief: dict[str, Any]) -> dict[str, Any]:
    req = brief.get("output_requirement", {})
    naming_count = int(req.get("naming_count", 4))
    slogan_count = int(req.get("slogan_count", 3))
    story_length = int(req.get("story_length", 300))

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "brand_names": {
                "type": "array",
                "minItems": naming_count,
                "maxItems": naming_count,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "meaning_origin": {"type": "string"},
                        "brand_image": {"type": "string"},
                        "story": {
                            "type": "string",
                            "description": f"한국어 {story_length}자 안팎의 네이밍 스토리",
                        },
                        "recommended_slogan": {"type": "string"},
                    },
                    "required": [
                        "name", "meaning_origin", "brand_image",
                        "story", "recommended_slogan",
                    ],
                },
            },
            "slogans": {
                "type": "array",
                "minItems": slogan_count,
                "maxItems": slogan_count,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "slogan": {"type": "string"},
                        "intention": {"type": "string"},
                    },
                    "required": ["slogan", "intention"],
                },
            },
            "top_recommendation": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "slogan": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["name", "slogan", "reason"],
            },
        },
        "required": ["brand_names", "slogans", "top_recommendation"],
    }


def generate_brand_elements(brief: dict[str, Any], model: str) -> dict[str, Any]:
    client = OpenAI()
    schema = get_schema(brief)

    system_prompt = """당신은 한국어 브랜드 네이밍과 카피라이팅 전문가입니다.
사용자가 제공한 JSON 브리프만 근거로 수제 디저트 카페의 브랜드 요소를 만드세요.
이름은 발음하기 쉽고 기억에 남아야 하며, 의미와 유래를 정직하게 설명하세요.
상표·도메인 등록 가능 여부는 확인하지 않았으므로 가능하다고 단정하지 마세요.
모든 결과는 한국어로 작성하고, 요청된 개수와 JSON 스키마를 정확히 지키세요.
슬로건은 짧고 강렬하되 브랜드의 톤앤매너를 반영하세요."""

    user_prompt = "다음 JSON 브리프를 분석해 브랜드 네이밍과 슬로건을 생성하세요.\n\n" + json.dumps(
        brief, ensure_ascii=False, indent=2
    )

    response = client.chat.completions.create(
        model=model,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "brand_elements",
                "strict": True,
                "schema": schema,
            },
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return json.loads(response.choices[0].message.content)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON 브리프 기반 브랜드 요소 생성기")
    parser.add_argument("brief", help="입력 JSON 브리프 파일 경로")
    parser.add_argument("--output", default="brand_result.json", help="결과 JSON 파일 경로")
    parser.add_argument("--model", default=os.getenv("BRAND_MODEL", DEFAULT_MODEL))
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY 환경변수를 먼저 설정하세요.")

    try:
        brief = load_brief(args.brief)
        result = generate_brand_elements(brief, args.model)
        Path(args.output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"생성 완료: {args.output}")
    except Exception as exc:
        sys.exit(f"오류: {exc}")


if __name__ == "__main__":
    main()
