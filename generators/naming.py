def generate_naming(brief, llm_client):
    """
    [담당: 팀원] 브랜드 네이밍 후보 생성 (기능 요구사항 3번)

    입력: brief (dict) — topic/target/keywords/tone/naming_count 등
          llm_client — llm_client.generate_json(system_prompt, user_prompt)로 호출

    반환 형식 (main.py 및 결과 저장 로직과 맞춰야 함):
        [
          {"name": "브랜드명", "meaning": "의미/유래 설명"},
          ...
        ]  # 개수는 brief["naming_count"]

    실패 시에는 llm_client 쪽에서 LLMError를 raise하며, main.py의 run_step()이
    이를 잡아 에러 메시지를 출력하고 다음 단계로 넘어가므로 이 함수 안에서
    별도로 try/except를 감쌀 필요는 없다 (원하면 감싸도 무방).

    TODO(팀원): 아래에 실제 프롬프트 구성 + llm_client.generate_json() 호출 구현
    """
    raise NotImplementedError("네이밍 생성 로직이 아직 구현되지 않았습니다 (담당 팀원 작업 예정).")
