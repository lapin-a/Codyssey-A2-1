def generate_logos(brief, naming, color_palette, image_client, output_dir):
    """
    [담당: 팀원] 로고 시안 생성 (기능 요구사항 7번)

    입력: brief (dict) — topic/tone/keywords/logo_concepts_count 등
          naming — generate_naming()의 결과 [{"name":..., "meaning":...}, ...] (실패 시 빈 리스트일 수 있음)
          color_palette — generate_color_palette()의 결과 {"main":[...], "sub":[...]} (실패 시 빈 dict일 수 있음)
          image_client — image_client.generate_image(prompt, save_path)로 호출
          output_dir — 이미지를 저장할 폴더 경로 (예: os.path.join(output_dir, "logo_1.png"))

    반환 형식:
        ["output/logo_1.png", "output/logo_2.png", ...]  # 저장에 성공한 파일 경로만 포함

    주의:
    - naming, color_palette는 다른 팀원 단계가 실패하면 빈 값으로 들어올 수 있으므로
      비어 있는 경우를 대비한 fallback 문구를 프롬프트에 넣는 것을 권장.
    - 로고를 여러 장(2~3개) 생성하므로, 한 장 실패가 전체를 막지 않도록
      이미지 1장 생성마다 image_client.ImageGenError를 개별적으로 잡아 처리할 것
      (예: 아래 뼈대의 for 루프 참고).

    TODO(팀원): 아래에 실제 프롬프트 구성 + image_client.generate_image() 호출 구현
    """
    # 참고용 뼈대 (그대로 사용해도 되고 자유롭게 수정 가능):
    #
    # import os
    # from image_client import ImageGenError
    #
    # saved_paths = []
    # count = brief.get("logo_concepts_count", 3)
    # for i in range(1, count + 1):
    #     prompt = "..."  # 브랜드명/톤앤매너/컬러를 반영한 로고 프롬프트 구성
    #     save_path = os.path.join(output_dir, f"logo_{i}.png")
    #     try:
    #         image_client.generate_image(prompt, save_path)
    #         saved_paths.append(save_path)
    #         print(f"[완료] 로고 시안 저장: {save_path}")
    #     except ImageGenError as e:
    #         print(f"[에러] 로고 시안 {i} 생성 실패: {e}")
    #         print(f"[알림] 로고 시안 {i}를 건너뛰고 다음 시안으로 계속 진행합니다.")
    # return saved_paths

    raise NotImplementedError("로고 시안 생성 로직이 아직 구현되지 않았습니다 (담당 팀원 작업 예정).")
