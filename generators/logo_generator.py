import json
import os

from dotenv import load_dotenv

# 1. .env 파일 로드
load_dotenv()


# =====================================================
# 내부 헬퍼
# =====================================================

def _get_logo_count(brief):
    """생성할 로고 개수를 brief에서 뽑아낸다.

    main.py는 평탄화된 brief(brief.py의 load_brief() 결과)를 넘겨주므로
    logo_concepts_count가 최상위에 있고, brief.json 원본(중첩 구조)을 그대로
    읽어 쓰는 단독 실행(__main__) 모드에서는 output_requirement 안에 있다.
    두 경우를 모두 지원한다.
    """
    if brief.get("logo_concepts_count") is not None:
        return brief["logo_concepts_count"]
    return brief.get("output_requirement", {}).get("logo_concepts_count", 3)


def _get_color_hexes(color_palette):
    """color_palette의 main/sub 색상에서 HEX 코드만 뽑아 리스트로 반환한다.

    generate_colors.py는 'main'을 단일 dict로 반환하지만, 컬러 팔레트 생성
    단계가 실패했을 때는 main.py가 {"main": {}, "sub": []} 형태의 빈 값을
    넘겨줄 수 있으므로 이 경우도 방어한다.
    """
    color_palette = color_palette or {}
    main = color_palette.get("main")
    sub = color_palette.get("sub") or []

    if isinstance(main, dict) and main:
        main_list = [main]
    elif isinstance(main, list):
        main_list = main
    else:
        main_list = []

    return [
        color["hex"]
        for color in (main_list + list(sub))
        if isinstance(color, dict) and color.get("hex")
    ]


def _build_logo_prompts(brief, top_recommendation, color_palette):
    """로고 시안 생성을 위한 프롬프트 목록을 만든다."""

    top_recommendation = top_recommendation or {}
    brand_name = top_recommendation.get("name") or "브랜드"
    slogan = top_recommendation.get("slogan") or ""

    topic = brief.get("topic", "")
    target = brief.get("target", "")
    keywords = ", ".join(brief.get("keywords", []) or [])
    tone = brief.get("tone", "")

    color_text = ", ".join(_get_color_hexes(color_palette)) or "지정된 컬러 없음(자유롭게 제안)"

    return [
        # -------------------------------------------------
        # 로고 시안 1
        # -------------------------------------------------
        f"""
브랜드명은 '{brand_name}'입니다.
슬로건은 '{slogan}'입니다.

업종:
{topic}

주요 타깃:
{target}

브랜드 키워드:
{keywords}

톤앤매너:
{tone}

브랜드 컬러:
{color_text}

수제 디저트와 따뜻한 휴식을 연상시키는
감성적인 카페 로고를 디자인해 주세요.

부드러운 곡선과 심플한 심볼을 사용하고,
직접 만든 디저트의 수제 감성과
조용하고 아늑한 공간의 느낌을 표현해 주세요.

브랜드명 '{brand_name}'이 잘 보이도록 하고,
카페 간판, 컵, 포장지에 사용할 수 있는
깔끔한 디자인으로 만들어 주세요.

화이트 배경,
미니멀한 벡터 로고,
복잡한 장식 없음,
세련되고 기억하기 쉬운 디자인.
""",
        # -------------------------------------------------
        # 로고 시안 2
        # -------------------------------------------------
        f"""
수제 디저트 카페 '{brand_name}'의
브랜드 로고를 디자인해 주세요.

슬로건:
'{slogan}'

타깃:
{target}

키워드:
{keywords}

톤:
{tone}

브랜드 컬러:
{color_text}

작은 케이크,
디저트 접시,
따뜻한 차 또는 커피의 느낌을
심플한 하나의 심볼로 표현해 주세요.

손으로 만든 듯한 따뜻함과
천천히 쉬어가는 여유를 표현합니다.

감성적이지만 지나치게 귀엽지 않고,
20~30대가 선호할 수 있는
세련된 카페 브랜드 스타일로 만들어 주세요.

화이트 배경,
minimal logo,
clean vector style,
simple icon,
premium handmade dessert cafe identity.
""",
        # -------------------------------------------------
        # 로고 시안 3
        # -------------------------------------------------
        f"""
브랜드명 '{brand_name}'을 중심으로 한
수제 디저트 카페 로고를 디자인해 주세요.

슬로건:
'{slogan}'

업종:
{topic}

브랜드 키워드:
{keywords}

톤앤매너:
{tone}

브랜드 컬러:
{color_text}

한글 브랜드명 '{brand_name}'이 중심이 되는
타이포그래피형 로고를 만들어 주세요.

천천히 여유롭게 머무는 느낌과,
수제 디저트의 따뜻하고 포근한 감성을
함께 표현해 주세요.

간판, 메뉴판, 디저트 패키지,
커피컵에 사용할 수 있는
단순하고 기억하기 쉬운 디자인이어야 합니다.

white background,
minimal typography logo,
flat vector style,
warm handmade feeling,
elegant and calm cafe branding.
""",
    ]


# =====================================================
# 공개 함수 — main.py는 이 함수를 그대로 import해서 사용한다.
# =====================================================

def generate_logos(brief, top_recommendation, color_palette, image_client, output_dir):
    """[담당: 팀원] 로고 시안 생성 (기능 요구사항 7번)

    brief: 브랜드 브리프. main.py는 평탄화된 형태(brief.py의 load_brief() 결과)를
           넘겨주고, 이 파일을 단독 실행할 때는 brief.json 원본(중첩 구조)을
           그대로 읽어서 넘긴다 — 둘 다 지원한다.
    top_recommendation: naming.py 결과의 top_recommendation ({"name", "slogan", "reason"}).
                        앞 단계가 실패하면 빈 dict가 들어올 수 있다.
    color_palette: generate_colors.py 결과의 color_palette ({"main": {...}, "sub": [...]}).
                   앞 단계가 실패하면 빈 dict가 들어올 수 있다.
    image_client: image_client.ImageClient 인스턴스 (generate_image(prompt, save_path) 메서드 필요).
    output_dir: 로고 PNG를 저장할 폴더 경로.

    반환: 저장에 성공한 파일 경로 리스트 (예: ["output/logo_01.png", ...]).
    로고 1장 생성 실패가 전체를 막지 않도록 for 루프 안에서 개별적으로 예외를 처리한다.
    """
    top_recommendation = top_recommendation or {}
    brand_name = top_recommendation.get("name") or "브랜드"
    slogan = top_recommendation.get("slogan") or ""

    logo_count = _get_logo_count(brief)
    prompts = _build_logo_prompts(brief, top_recommendation, color_palette)[:logo_count]

    os.makedirs(output_dir, exist_ok=True)

    print()
    print("=" * 50)
    print(f"{brand_name} 로고 이미지 생성 시작")
    print("=" * 50)
    print(f"브랜드명: {brand_name}")
    print(f"슬로건: {slogan}")
    print(f"생성할 로고 수: {len(prompts)}")
    print()

    saved_paths = []

    for i, prompt in enumerate(prompts, start=1):
        print(f"[{i}/{len(prompts)}] 로고 생성 중...")
        output_path = os.path.join(output_dir, f"logo_{i:02d}.png")

        try:
            image_client.generate_image(prompt, output_path)
        except Exception as error:
            print(f"로고 {i} 생성 실패")
            print("오류 내용:")
            print(error)
        else:
            print(f"저장 완료: {output_path}")
            saved_paths.append(output_path)

        print()

    print("=" * 50)
    print("로고 생성 작업 완료")
    print("=" * 50)
    print()

    return saved_paths


# =====================================================
# 단독 실행용 이미지 클라이언트
# (generate_colors.py / generate_story.py처럼 외부 파일 의존 없이
#  이 파일 하나로도 바로 실행할 수 있도록 최소 구현을 둔다.)
# =====================================================

class _StandaloneImageClient:
    """image_client.ImageClient와 동일한 인터페이스(generate_image)를 갖는
    단독 실행 전용 클라이언트. main.py를 통해 실행할 때는 쓰이지 않는다."""

    def __init__(self):
        import base64  # noqa: F401 (지역 임포트로 필요한 곳에서만 사용)
        self._base64 = base64

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)

    def generate_image(self, prompt, save_path):
        response = self._client.images.generate(
            model="gpt-image-1.5",
            prompt=prompt,
            size="1024x1024",
        )
        image_bytes = self._base64.b64decode(response.data[0].b64_json)

        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        with open(save_path, "wb") as image_file:
            image_file.write(image_bytes)


if __name__ == "__main__":
    try:
        # 1. brief.json 읽기
        with open("brief.json", "r", encoding="utf-8") as f:
            brief_data = json.load(f)

        # 2. brand_result.json 읽기
        with open("brand_result.json", "r", encoding="utf-8") as f:
            brand_result_data = json.load(f)

        top_recommendation_data = brand_result_data.get("top_recommendation", {})
        color_palette_data = brand_result_data.get("color_palette", {})

        # 3. 로고 생성
        image_client = _StandaloneImageClient()
        logo_files = generate_logos(
            brief_data,
            top_recommendation_data,
            color_palette_data,
            image_client,
            output_dir="output",
        )

        if logo_files:
            print("\n=== 로고 생성 결과 ===")
            print(json.dumps(logo_files, ensure_ascii=False, indent=2))

            # 4. brand_result_data 객체에 'logo_files' 키로 결과 저장
            brand_result_data["logo_files"] = logo_files

            # 5. brand_result.json 파일에 최종 업데이트 저장
            with open("brand_result.json", "w", encoding="utf-8") as f:
                json.dump(brand_result_data, f, ensure_ascii=False, indent=2)

            print("\n[성공] brand_result.json 파일에 'logo_files' 항목이 성공적으로 업데이트되었습니다.")
        else:
            print("\n[알림] 생성된 로고가 없습니다.")

    except FileNotFoundError as e:
        print(f"[Error] 필요한 JSON 파일을 찾을 수 없습니다: {e.filename}")
    except json.JSONDecodeError:
        print("[Error] JSON 파일의 형식이 올바르지 않습니다.")
    except ValueError as e:
        print(f"[Error] {e}")
