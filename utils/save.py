import json
import os


def save_result_json(result, output_dir):
    """
    [담당: 나] 텍스트 결과를 brand_result.json으로 저장 (기능 요구사항 8번)
    실패 시(디스크 쓰기 오류 등) 예외를 발생시킨다. main.py의 run_step()이 처리한다.
    """
    save_path = os.path.join(output_dir, "brand_result.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[완료] 텍스트 결과 저장: {save_path}")
    return save_path
