def generate_color_palette(brief, llm_client):
    """
    [담당: 팀원] 컬러 팔레트 생성 (기능 요구사항 6번)

    입력: brief (dict) — topic/target/keywords/tone/main_colors/sub_colors 등
          llm_client — llm_client.generate_json(system_prompt, user_prompt)로 호출

    반환 형식 (palette_image.py 및 결과 저장 로직과 맞춰야 함):
        {
          "main": [{"hex": "#RRGGBB", "reason": "선택 이유"}],   # 개수는 brief["main_colors"]
          "sub": [{"hex": "#RRGGBB", "reason": "선택 이유"}, ...]  # 개수는 brief["sub_colors"]
        }

    실패 시에는 llm_client 쪽에서 LLMError를 raise하며, main.py의 run_step()이
    이를 잡아 에러 메시지를 출력하고 다음 단계로 넘어가므로 이 함수 안에서
    별도로 try/except를 감쌀 필요는 없다 (원하면 감싸도 무방).

    TODO(팀원): 아래에 실제 프롬프트 구성 + llm_client.generate_json() 호출 구현
    """
    raise NotImplementedError("컬러 팔레트 생성 로직이 아직 구현되지 않았습니다 (담당 팀원 작업 예정).")
