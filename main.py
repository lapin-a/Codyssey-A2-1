import os

from config import DEFAULT_OUTPUT_DIR
from brief import load_brief
from llm_client import LLMClient
from image_client import ImageClient

# 팀원 담당 (기능 요구사항 3~7번, 8번 중 팔레트 시각화)
from generators.naming import generate_naming
from generators.slogan import generate_slogan
from generators.generate_story import generate_brand_story
from generators.generate_colors import generate_color_recommendations
from generators.logo import generate_logos
from generators.palette_image import save_palette_image  # 컬러 팔레트 시각화(8번)는 다른 담당자 영역

# 내 담당 (기능 요구사항 1, 2, 8번 중 텍스트 결과 저장, 9, 10번)
from utils.save import save_result_json


def get_user_input():
    """기능 요구사항 1번: 대화형 사용자 입력"""
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
    naming/slogan/logo(팀원 담당, 실패 시 예외를 raise하는 방식)와 결과 저장(내 담당)이
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
    generate_story.py / generate_colors.py는 brief.json 원본의 중첩 구조
    (output_requirement.story_length, output_requirement.color_palette.main_colors 등)를
    그대로 기대한다. 반면 brief.py의 load_brief()는 다른 팀원 모듈(naming/slogan/logo)이
    쓰기 편하도록 이미 평탄화(flatten)한 구조를 반환한다.

    두 파일을 수정하지 않고 그대로 쓰기 위해, 평탄화된 brief를 다시 중첩 구조로
    복원해서 넘겨준다. (naming/slogan/logo에는 기존처럼 평탄화된 brief를 그대로 전달)
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
    # 참고: generate_story.py / generate_colors.py는 내부적으로 자체 OpenAI 클라이언트를
    # 만들어 쓰므로 아래 llm_client는 naming/slogan에만 사용된다.
    llm_client = LLMClient()
    image_client = ImageClient()

    print("\n[1/6] 브랜드 네이밍 생성 중... (담당: 팀원)")
    naming = run_step("네이밍 생성", generate_naming, brief, llm_client, fallback=[])

    print("\n[2/6] 슬로건 생성 중... (담당: 팀원)")
    slogan = run_step("슬로건 생성", generate_slogan, brief, llm_client, fallback=[])

    print("\n[3/6] 브랜드 스토리 생성 중... (담당: 팀원)")
    story_result = run_soft_step(
        "브랜드 스토리 생성", generate_brand_story, legacy_brief, fallback=None
    )
    story = story_result["story"] if story_result else ""

    print("\n[4/6] 컬러 팔레트 생성 중... (담당: 팀원)")
    color_result = run_soft_step(
        "컬러 팔레트 생성", generate_color_recommendations, legacy_brief, fallback=None
    )
    # generate_colors.py 반환 형식: {"color_palette": {"main": {...}, "sub": [...]}}
    color_palette = color_result["color_palette"] if color_result else {"main": {}, "sub": []}

    print("\n[5/6] 로고 시안 생성 중... (담당: 팀원)")
    logo_paths = run_step(
        "로고 시안 생성", generate_logos, brief, naming, color_palette, image_client, output_dir,
        fallback=[],
    )

    print("\n[6/6] 팔레트 이미지 시각화 중... (담당: 팀원)")
    # 컬러 팔레트 생성(4단계)과는 다른 담당자의 영역. generators/palette_image.py는
    # 실패 시 예외를 raise하는 방식이므로 기존 run_step()으로 처리한다.
    run_step("컬러 팔레트 이미지 저장", save_palette_image, color_palette, output_dir)

    print("\n[결과 저장] 최종 텍스트 결과 저장 중... (담당: 나)")

    final_result = {
        "brief": brief,
        "naming": naming,
        "slogan": slogan,
        "story": story,
        "color_palette": color_palette,
        "logo_files": logo_paths,
    }
    run_step("결과 JSON 저장", save_result_json, final_result, output_dir)

    print("\n=== 완료 ===")
    print(f"결과물은 '{output_dir}' 폴더를 확인하세요.")


if __name__ == "__main__":
    main()
