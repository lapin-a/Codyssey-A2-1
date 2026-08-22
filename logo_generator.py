import json
import os
import base64

from openai import OpenAI
from dotenv import load_dotenv


# =====================================================
# 1. .env 파일에서 API 키 불러오기
# =====================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요."
    )

client = OpenAI(api_key=api_key)


# =====================================================
# 2. brief.json 읽기
# =====================================================

with open("brief.json", "r", encoding="utf-8") as file:
    brief = json.load(file)


# =====================================================
# 3. color.json 읽기
# =====================================================

with open("color.json", "r", encoding="utf-8") as file:
    color_data = json.load(file)


# =====================================================
# 4. 브랜드 정보
# =====================================================

brand_name = "느루"
slogan = "천천히, 달콤하게."


# =====================================================
# 5. 컬러 정보 가져오기
# =====================================================

palette = color_data["color_palette"]

main_color = palette["main"]["hex"]

sub_colors = [
    color["hex"]
    for color in palette["sub"]
]

all_colors = [main_color] + sub_colors

color_text = ", ".join(all_colors)


# =====================================================
# 6. brief.json 정보 가져오기
# =====================================================

topic = brief["topic"]
target = brief["target"]

keywords = ", ".join(
    brief["keywords"]
)

tone = brief["tone"]

logo_count = brief[
    "output_requirement"
]["logo_concepts_count"]


# =====================================================
# 7. 로고 생성용 프롬프트 만들기
# =====================================================

logo_prompts = [

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

브랜드명 '느루'가 잘 보이도록 하고,
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

한글 '느루'가 중심이 되는
타이포그래피형 로고를 만들어 주세요.

느루가 가진
'천천히, 여유 있게'라는 이미지를 표현하고,
수제 디저트의 따뜻하고 포근한 감성을 더해 주세요.

간판, 메뉴판, 디저트 패키지,
커피컵에 사용할 수 있는
단순하고 기억하기 쉬운 디자인이어야 합니다.

white background,
minimal typography logo,
flat vector style,
warm handmade feeling,
elegant and calm cafe branding.
"""
]


# =====================================================
# 8. output 폴더 생성
# =====================================================

os.makedirs(
    "output",
    exist_ok=True
)


# =====================================================
# 9. 로고 생성 시작
# =====================================================

print()
print("=" * 50)
print("느루 로고 이미지 생성 시작")
print("=" * 50)

print(f"브랜드명: {brand_name}")
print(f"슬로건: {slogan}")
print(f"생성할 로고 수: {logo_count}")

print()


# =====================================================
# 10. 로고를 하나씩 생성
# =====================================================

for i, prompt in enumerate(
    logo_prompts[:logo_count],
    start=1
):

    print(
        f"[{i}/{logo_count}] "
        f"로고 생성 중..."
    )

    try:

        # ---------------------------------------------
        # OpenAI 이미지 생성 API 호출
        # ---------------------------------------------

        result = client.images.generate(
            model="gpt-image-1.5",
            prompt=prompt,
            size="1024x1024"
        )


        # ---------------------------------------------
        # 이미지 데이터 가져오기
        # ---------------------------------------------

        image_base64 = (
            result.data[0].b64_json
        )

        image_bytes = base64.b64decode(
            image_base64
        )


        # ---------------------------------------------
        # 저장할 파일 이름
        # ---------------------------------------------

        output_path = (
            f"output/logo_{i:02d}.png"
        )


        # ---------------------------------------------
        # PNG 파일 저장
        # ---------------------------------------------

        with open(
            output_path,
            "wb"
        ) as image_file:

            image_file.write(
                image_bytes
            )


        print(
            f"저장 완료: {output_path}"
        )


    except Exception as error:

        print(
            f"로고 {i} 생성 실패"
        )

        print(
            "오류 내용:"
        )

        print(
            error
        )

    print()


# =====================================================
# 11. 완료
# =====================================================

print("=" * 50)
print("로고 생성 작업 완료")
print("=" * 50)

print()

print("결과 폴더:")

print(
    "output/logo_01.png"
)

print(
    "output/logo_02.png"
)

print(
    "output/logo_03.png"
)