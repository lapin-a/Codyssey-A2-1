import os

from image_client import ImageGenError


def _pick_brand_name(naming, brief):
    """naming 인자에서 대표 브랜드명/설명을 뽑는다.

    naming.py(generate_brand_elements)의 top_recommendation 형식
    {"name":..., "slogan":..., "reason":...} 을 우선 지원하고,
    과거 generate_naming() 형식인 [{"name":..., "meaning":...}, ...] 리스트도
    호환을 위해 함께 지원한다. naming 단계가 실패해 빈 값으로 들어오면
    brief의 topic으로 대체한다."""
    if isinstance(naming, dict) and naming:
        name = naming.get("name", "")
        detail = naming.get("reason") or naming.get("slogan", "")
        return name, detail

    if isinstance(naming, list) and naming:
        top = naming[0]
        return top.get("name", ""), top.get("meaning", "")

    return brief.get("topic", "브랜드"), ""


def _extract_hex_list(color_palette):
    """color_palette(generate_color_palette 결과)에서 hex 코드 목록을 뽑는다.
    main이 dict(단일 색)로 오는 경우와 list로 오는 경우를 모두 지원하고,
    color_palette 단계가 실패해 빈 dict로 들어와도 동작하도록 방어한다."""
    color_palette = color_palette or {}
    main = color_palette.get("main")
    sub = color_palette.get("sub") or []

    if isinstance(main, dict) and main:
        main_list = [main]
    elif isinstance(main, list):
        main_list = main
    else:
        main_list = []

    return [c["hex"] for c in (main_list + list(sub)) if isinstance(c, dict) and c.get("hex")]


def _build_logo_prompt(idx, brand_name, brand_meaning, brief, color_text):
    topic = brief.get("topic", "") or "브랜드"
    target = brief.get("target", "") or "특정 타깃 제한 없음"
    keywords = ", ".join(brief.get("keywords", [])) or "없음"
    tone = brief.get("tone", "") or "자유로운 톤"

    return f"""
브랜드명: {brand_name or "(미정)"}
브랜드명 의미: {brand_meaning or "없음"}

업종: {topic}
주요 타깃: {target}
브랜드 키워드: {keywords}
톤앤매너: {tone}
브랜드 컬러: {color_text}

위 정보를 반영한 로고 시안 {idx}번을 디자인해 주세요.
화이트 배경의 미니멀한 벡터 로고, 심플한 심볼과 타이포그래피를 활용하고
간판·패키지·명함 등 다양한 곳에 활용할 수 있는 깔끔하고 기억하기 쉬운 디자인으로
만들어 주세요. 복잡한 장식은 넣지 말아 주세요.
""".strip()


def generate_logos(brief, naming, color_palette, image_client, output_dir):
    """
    [담당: 팀원] 로고 시안 생성 (기능 요구사항 7번)

    입력: brief (dict) — topic/tone/keywords/logo_concepts_count 등
          naming — naming.py(generate_brand_elements)의 top_recommendation
                   {"name":..., "slogan":..., "reason":...} (실패 시 빈 dict일 수 있음)
                   과거 generate_naming() 형식인 리스트도 함께 지원한다.
          color_palette — generate_color_recommendations()의 결과 {"main":..., "sub":[...]} (실패 시 빈 dict일 수 있음)
          image_client — image_client.generate_image(prompt, save_path)로 호출
          output_dir — 이미지를 저장할 폴더 경로 (예: os.path.join(output_dir, "logo_1.png"))

    반환 형식:
        ["output/logo_1.png", "output/logo_2.png", ...]  # 저장에 성공한 파일 경로만 포함
    """
    saved_paths = []

    count = brief.get("logo_concepts_count", 3)
    brand_name, brand_meaning = _pick_brand_name(naming, brief)
    hex_list = _extract_hex_list(color_palette)
    color_text = ", ".join(hex_list) if hex_list else "브랜드 이미지에 어울리는 색상을 자유롭게 선택"

    for i in range(1, count + 1):
        prompt = _build_logo_prompt(i, brand_name, brand_meaning, brief, color_text)
        save_path = os.path.join(output_dir, f"logo_{i}.png")

        try:
            image_client.generate_image(prompt, save_path)
            saved_paths.append(save_path)
            print(f"[완료] 로고 시안 저장: {save_path}")
        except ImageGenError as e:
            print(f"[에러] 로고 시안 {i} 생성 실패: {e}")
            print(f"[알림] 로고 시안 {i}를 건너뛰고 다음 시안으로 계속 진행합니다.")

    return saved_paths
