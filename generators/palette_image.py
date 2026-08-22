import os


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

    참고: matplotlib 등 원하는 라이브러리로 자유롭게 구현 가능
        (예: matplotlib.patches.Rectangle로 색상 스와치를 그리는 방식)

    TODO(팀원): 아래에 실제 시각화 + 저장 로직 구현
    """
    raise NotImplementedError("컬러 팔레트 시각화 로직이 아직 구현되지 않았습니다 (담당 팀원 작업 예정).")
