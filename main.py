import os

from config import DEFAULT_OUTPUT_DIR
from brief import load_brief
from llm_client import LLMClient
from image_client import ImageClient

# 팀원 담당 (기능 요구사항 3~7번, 8번 중 팔레트 시각화)
from generators.naming import generate_naming
from generators.slogan import generate_slogan
from generators.story import generate_story
from generators.color import generate_color_palette
from generators.logo import generate_logos
from generators.palette_image import save_palette_image

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
    기능 요구사항 9번: 에러 처리 공통 로직.
    한 단계를 실행하고, 어떤 단계에서 어떤 오류가 발생했는지 출력한 뒤
    fallback 값을 반환해 파이프라인이 끊기지 않고 다음 단계로 계속 진행되게 한다.
    naming/slogan/story/color(팀원 담당)와 palette_image/save(내 담당) 모두
    이 함수를 통해 실행되므로 에러 출력 형식이 일관된다.
    """
    try:
        result = func(*args, **kwargs)
        print(f"[완료] {step_name}")
        return result
    except Exception as e:
        print(f"[에러] '{step_name}' 단계에서 오류가 발생했습니다: {e}")
        print(f"[알림] '{step_name}' 단계를 건너뛰고 다음 단계로 계속 진행합니다.")
        return fallback


def main():
    brief_path, output_dir = get_user_input()
    os.makedirs(output_dir, exist_ok=True)

    # 기능 요구사항 2번: 브랜드 브리프 입력 (JSON)
    brief = load_brief(brief_path)

    # 기능 요구사항 10번: API 키는 환경 변수에서 읽어옴 (config.py 참고)
    llm_client = LLMClient()
    image_client = ImageClient()

    print("\n[1/6] 브랜드 네이밍 생성 중... (담당: 팀원)")
    naming = run_step("네이밍 생성", generate_naming, brief, llm_client, fallback=[])

    print("\n[2/6] 슬로건 생성 중... (담당: 팀원)")
    slogan = run_step("슬로건 생성", generate_slogan, brief, llm_client, fallback=[])

    print("\n[3/6] 브랜드 스토리 생성 중... (담당: 팀원)")
    story = run_step("브랜드 스토리 생성", generate_story, brief, llm_client, fallback="")

    print("\n[4/6] 컬러 팔레트 생성 중... (담당: 팀원)")
    color_palette = run_step(
        "컬러 팔레트 생성", generate_color_palette, brief, llm_client,
        fallback={"main": [], "sub": []},
    )

    print("\n[5/6] 로고 시안 생성 중... (담당: 팀원)")
    logo_paths = run_step(
        "로고 시안 생성", generate_logos, brief, naming, color_palette, image_client, output_dir,
        fallback=[],
    )

    print("\n[6/6] 팔레트 이미지 시각화 중... (담당: 팀원)")
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
