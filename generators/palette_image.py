import os

import matplotlib

matplotlib.use("Agg")  # 화면 없이(서버/CLI 환경) PNG 저장을 위한 백엔드

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

plt.rcParams["axes.unicode_minus"] = False

# 컬러 이름(한글)이 깨지지 않도록, 실행 환경에 설치된 한글 폰트가 있으면 사용한다.
# (환경마다 설치된 폰트가 달라서 하나만 하드코딩하면 다른 OS에서 깨질 수 있음)
_KOREAN_FONT_CANDIDATES = [
    "Malgun Gothic",   # Windows
    "AppleGothic",     # macOS
    "NanumGothic",      # Linux (나눔고딕이 설치된 경우)
    "Noto Sans CJK KR",
    "Noto Sans KR",
]


def _apply_korean_font():
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in _KOREAN_FONT_CANDIDATES:
        if name in available:
            plt.rcParams["font.family"] = name
            return
    # 위 후보 중 설치된 폰트가 없으면 기본 폰트로 진행한다.
    # (한글 색상 이름이 네모(□)로 보일 수 있지만, PNG 생성 자체는 실패하지 않는다.)


def _normalize_colors(color_palette):
    """
    generate_color_palette()의 반환 형식을 팔레트 스와치를 그리기 위한
    단일 리스트로 정규화한다.

    color_palette: {"main": {...} 또는 [{...}], "sub": [{...}, ...]}
    - generate_colors.py(실제 구현)는 main을 단일 dict로 반환하고,
      README의 이상적인 인터페이스는 main을 리스트로 정의하고 있어
      둘 다 대응하도록 처리한다.
    - 컬러 팔레트 생성 단계가 실패했을 경우 빈 dict({"main": {}, "sub": []})가
      들어올 수 있으므로 이 경우도 방어한다.
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

    colors = main_list + list(sub)
    # hex 코드가 없는 항목은 스와치를 그릴 수 없으므로 제외
    return [c for c in colors if isinstance(c, dict) and c.get("hex")]


def save_palette_image(color_palette, output_dir):
    """
    [담당: 팀원] 컬러 팔레트 시각화 → PNG 저장 (기능 요구사항 8번 중 팔레트 시각화 부분)

    color_palette: {"main": [{"hex":..., "reason":...}], "sub": [...]}
    (컬러 팔레트 생성(6번)이 실패하면 빈 dict {"main": [], "sub": []}가 들어올 수 있음
     — 이 경우를 대비한 처리를 넣을 것)

    저장 경로: os.path.join(output_dir, "palette.png") 권장 (main.py의 결과 요약과 맞추기 위함)
    반환 형식: 저장한 파일 경로(str) — main.py에서는 반환값을 직접 쓰진 않지만,
              나중에 확장할 수 있으니 반환해두는 걸 권장.

    실패 시(색상 데이터 없음, 렌더링 오류 등) 예외를 발생시키면 된다.
    main.py의 run_step()이 이를 잡아 에러를 출력하고 다음 단계로 진행한다.
    """
    colors = _normalize_colors(color_palette)
    if not colors:
        raise ValueError("시각화할 컬러 팔레트 데이터가 없습니다 (color_palette가 비어 있음).")

    _apply_korean_font()

    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1.5)
    ax.axis("off")

    for i, color in enumerate(colors):
        hex_code = color.get("hex", "")
        color_name = color.get("name", "")

        # 컬러 사각형 만들기
        rectangle = Rectangle(
            (i, 0.45),
            1,
            0.8,
            facecolor=hex_code,
        )
        ax.add_patch(rectangle)

        # HEX 코드 표시
        ax.text(
            i + 0.5,
            0.30,
            hex_code,
            ha="center",
            va="center",
            fontsize=11,
        )

        # 컬러 이름 표시 (없으면 생략)
        if color_name:
            ax.text(
                i + 0.5,
                0.12,
                color_name,
                ha="center",
                va="center",
                fontsize=10,
            )

    plt.title("Brand Color Palette", fontsize=18)

    output_path = os.path.join(output_dir, "palette.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print("컬러 팔레트 이미지 생성 완료")
    print(output_path)

    return output_path
