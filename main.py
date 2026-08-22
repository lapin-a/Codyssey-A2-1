import os
import sys

from config import DEFAULT_OUTPUT_DIR
from brief import load_brief
from image_client import ImageClient

# 팀원 담당 (기능 요구사항 3~7번, 8번 중 팔레트 시각화)
# naming.py는 브랜드명+슬로건+최종 추천(top_recommendation)을 한 번에 생성한다
# (generate_brand_elements). generate_colors.py / generate_story.py는 이제
# naming.py의 결과(brand_result)를 받아서 그 안의 top_recommendation을 활용한다.
from generators.naming import generate_brand_elements, DEFAULT_MODEL as NAMING_DEFAULT_MODEL
from generators.generate_story import generate_brand_story
from generators.generate_colors import generate_color_recommendations
from generators.logo import generate_logos
from generators.palette_image import save_palette_image  # 컬러 팔레트 시각화(8번)는 다른 담당자 영역

# 내 담당 (기능 요구사항 1, 2, 8번 중 텍스트 결과 저장, 9, 10번)
from utils.save import save_result_json


def get_user_input():
    """기능 요구사항 1번: 대화형 사용자 입력

    편의를 위해 명령줄 인자도 함께 지원한다:
        python main.py <brief.json 경로> [출력 폴더 경로]
    인자가 없으면 기존처럼 input()으로 물어본다.
    """
    if len(sys.argv) >= 2:
        brief_path = sys.argv[1].strip()
        output_dir = sys.argv[2].strip() if len(sys.argv) >= 3 else ""
    else:
        print("=== AI 브랜드 생성기 ===")
        brief_path = input("브리프 JSON 파일 경로를 입력하세요: ").strip()
        output_dir = input(f"출력 폴더 경로를 입력하세요 (기본값: {DEFAULT_OUTPUT_DIR}): ").strip()

    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
    return brief_path, output_dir


def run_step(step_name, func, *args, fallback=None, **kwargs):
    """
    기능 요구사항 9번: 에러 처리 공통 로직 (예외를 던지는 함수용).
    한 단계를 실행하고, 어떤 단계에서 어떤 오류가 발생했는지 출력한 뒤
    fallback 값을 반환해 파이프라인이 끊기지 않고 다음 단계로 계속 진행되게 한다.
    naming/logo(팀원 담당, 실패 시 예외를 raise하는 방식)와 결과 저장(내 담당)이
    이 함수를 사용한다.
    """
    try:
        result = func(*args, **kwargs)
        print(f"[완료] {step_name}")
        return result
    except Exception as e:
        print(f"[에러] '{step_name}' 단계에서 오류가 발생했습니다: {e}")
        print(f"[알림] '{step_name}' 단계를 건너뛰고 다음 단계로 계속 진행합니다.")
        return fallback


def run_soft_step(step_name, func, *args, fallback=None, **kwargs):
    """
    기능 요구사항 9번: 에러 처리 공통 로직 (내부에서 에러를 이미 출력하고 예외 대신
    None을 반환하는 함수용 — generate_story.py / generate_colors.py가 이 방식).

    이 함수들은:
      - API 키가 아예 없으면 ValueError를 raise
      - 그 외 API 통신/파싱 오류는 자체적으로 [Error] 메시지를 출력하고 None을 반환
    두 경우 모두 여기서 잡아서 fallback으로 통일하고, 파이프라인은 계속 진행된다.
    """
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        print(f"[에러] '{step_name}' 단계에서 예외가 발생했습니다: {e}")
        print(f"[알림] '{step_name}' 단계를 건너뛰고 다음 단계로 계속 진행합니다.")
        return fallback

    if result is None:
        print(f"[알림] '{step_name}' 단계가 결과 없이 종료되었습니다 (위 [Error] 메시지 참고).")
        print(f"[알림] '{step_name}' 단계를 건너뛰고 다음 단계로 계속 진행합니다.")
        return fallback

    print(f"[완료] {step_name}")
    return result


def _to_legacy_brief(brief):
    """
    naming.py / generate_story.py / generate_colors.py는 brief.json 원본의 중첩 구조
    (output_requirement.naming_count, output_requirement.color_palette.main_colors 등)를
    그대로 기대한다. 반면 brief.py의 load_brief()는 다른 팀원 모듈이 쓰기 편하도록
    이미 평탄화(flatten)한 구조를 반환한다.

    해당 파일들을 수정하지 않고 그대로 쓰기 위해, 평탄화된 brief를 다시 중첩 구조로
    복원해서 넘겨준다.
    """
    return {
        **brief,
        "output_requirement": {
            "naming_count": brief.get("naming_count"),
            "slogan_count": brief.get("slogan_count"),
            "story_length": brief.get("story_length"),
            "color_palette": {
                "main_colors": brief.get("main_colors"),
                "sub_colors": brief.get("sub_colors"),
            },
            "logo_concepts_count": brief.get("logo_concepts_count"),
        },
    }


def main():
    brief_path, output_dir = get_user_input()
    os.makedirs(output_dir, exist_ok=True)

    # 기능 요구사항 2번: 브랜드 브리프 입력 (JSON)
    brief = load_brief(brief_path)
    legacy_brief = _to_legacy_brief(brief)

    # 기능 요구사항 10번: API 키는 환경 변수에서 읽어옴 (config.py 참고)
    # 참고: naming.py / generate_story.py / generate_colors.py는 내부적으로 자체
    # OpenAI 클라이언트를 만들어 쓰므로, 여기서는 로고 생성에 쓰는 image_client만 준비한다.
    image_client = ImageClient()

    print("\n[1/5] 브랜드 네이밍 + 슬로건 생성 중... (담당: 팀원)")
    # naming.py는 이름/슬로건/최종 추천(top_recommendation)을 한 번에 생성한다.
    naming_model = os.getenv("BRAND_MODEL", NAMING_DEFAULT_MODEL)
    brand_result = run_step(
        "브랜드 네이밍 생성", generate_brand_elements, legacy_brief, naming_model,
        fallback={"brand_names": [], "slogans": [], "top_recommendation": {}},
    )
    naming = brand_result.get("brand_names", [])
    slogan = brand_result.get("slogans", [])

    print("\n[2/5] 브랜드 스토리 생성 중... (담당: 팀원)")
    # generate_story.py는 이제 top_recommendation이 담긴 brand_result를 함께 받는다.
    story_result = run_soft_step(
        "브랜드 스토리 생성", generate_brand_story, legacy_brief, brand_result, fallback=None
    )
    story = story_result["story"] if story_result else ""

    print("\n[3/5] 컬러 팔레트 생성 중... (담당: 팀원)")
    # generate_colors.py도 마찬가지로 brand_result를 함께 받는다.
    color_result = run_soft_step(
        "컬러 팔레트 생성", generate_color_recommendations, legacy_brief, brand_result, fallback=None
    )
    # generate_colors.py 반환 형식: {"color_palette": {"main": {...}, "sub": [...]}}
    color_palette = color_result["color_palette"] if color_result else {"main": {}, "sub": []}

    print("\n[4/5] 로고 시안 생성 중... (담당: 팀원)")
    # naming.py의 결과 중 top_recommendation(최종 추천 브랜드명)을 로고 생성에 활용한다.
    top_recommendation = brand_result.get("top_recommendation", {})
    logo_paths = run_step(
        "로고 시안 생성", generate_logos, brief, top_recommendation, color_palette, image_client, output_dir,
        fallback=[],
    )

    print("\n[5/5] 팔레트 이미지 시각화 중... (담당: 팀원)")
    # 컬러 팔레트 생성(3단계)과는 다른 담당자의 영역. generators/palette_image.py는
    # 실패 시 예외를 raise하는 방식이므로 기존 run_step()으로 처리한다.
    run_step("컬러 팔레트 이미지 저장", save_palette_image, color_palette, output_dir)

    print("\n[결과 저장] 최종 텍스트 결과 저장 중... (담당: 나)")

    final_result = {
        "brief": brief,
        "naming": naming,
        "slogan": slogan,
        "top_recommendation": top_recommendation,
        "story": story,
        "color_palette": color_palette,
        "logo_files": logo_paths,
    }
    run_step("결과 JSON 저장", save_result_json, final_result, output_dir)

    print("\n=== 완료 ===")
    print(f"결과물은 '{output_dir}' 폴더를 확인하세요.")


if __name__ == "__main__":
    main()
