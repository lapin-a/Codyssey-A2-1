# 브랜드 생성기 CLI — 팀원 작업 가이드

## 프로젝트 구조 및 담당

| 파일 | 기능 요구사항 | 담당 |
|---|---|---|
| `generators/naming.py` | 3. 브랜드 네이밍 생성 | 오서진 |
| `generators/slogan.py` | 4. 슬로건 생성 | 오서진 |
| `generators/story.py` | 5. 브랜드 스토리 생성 | 김지혜 |
| `generators/color.py` | 6. 컬러 팔레트 생성 | 김지혜 |
| `generators/logo.py` | 7. 로고 시안 생성 | 이창진 |
| `generators/palette_image.py` | 8. 컬러 팔레트 시각화(PNG) | 이창진 |
| `main.py`, `brief.py`, `config.py` | 1, 2, 9, 10. 입력/에러처리/API키관리 | 육성준 |
| `utils/save.py` | 8. 텍스트 결과 저장(JSON) | 육성준 |

각자 맡은 `generators/*.py` 파일 안의 `raise NotImplementedError(...)` 한 줄만 지우고, 그 자리에 실제 로직을 채우면 됩니다. **함수 시그니처(입력 인자)와 반환 형식은 절대 바꾸지 말아주세요** — `main.py`가 그 형식을 그대로 받아서 다음 단계에 넘기고, 최종 `brand_result.json`에 그대로 들어갑니다.

## 실행 방법

```bash
pip install -r requirements.txt --break-system-packages   # 또는 가상환경에서 pip install -r requirements.txt
cp .env.example .env   # 발급받은 API 키를 채워넣기
python main.py
```

실행하면 브리프 파일 경로(예: `brief_example.json`)와 출력 폴더 경로를 입력받습니다.

## 공용 도구

### `llm_client.py` — `LLMClient`
```python
from llm_client import LLMClient, LLMError

llm_client = LLMClient()
result = llm_client.generate_json(system_prompt, user_prompt)
# 성공 시 dict 반환, 실패 시 LLMError를 raise함 (직접 잡지 않아도 main.py가 처리)
```
- `system_prompt`, `user_prompt`는 여러분이 자유롭게 구성하면 됩니다.
- **LLM 응답은 반드시 JSON 문자열로만 받도록 프롬프트를 짜주세요.** (`generate_json`이 내부에서 `json.loads()`로 파싱합니다.)
- 실제 API 호출부(TODO 주석)는 아직 비어 있습니다 — 어떤 LLM provider를 쓸지 정해지면 그때 채워 넣거나, 먼저 이 부분을 구현해주셔도 됩니다.

### `image_client.py` — `ImageClient`
```python
from image_client import ImageClient, ImageGenError

image_client = ImageClient()
image_client.generate_image(prompt, save_path)
# 성공 시 save_path에 PNG 저장, 실패 시 ImageGenError를 raise함
```
- 로고 생성(`logo.py`)에서 사용합니다.
- 마찬가지로 실제 API 호출부는 TODO로 비어 있습니다.

## 각 함수 인터페이스

### `generate_naming(brief, llm_client)` — `naming.py`
- 반환: `[{"name": "브랜드명", "meaning": "의미 설명"}, ...]` (개수: `brief["naming_count"]`)

### `generate_slogan(brief, llm_client)` — `slogan.py`
- 반환: `["슬로건1", "슬로건2", ...]` (개수: `brief["slogan_count"]`)

### `generate_story(brief, llm_client)` — `story.py`
- 반환: `"브랜드 스토리 본문"` (문자열, `brief["story_length"]`자 내외)

### `generate_color_palette(brief, llm_client)` — `color.py`
- 반환: `{"main": [{"hex": "#RRGGBB", "reason": "..."}], "sub": [{"hex": "...", "reason": "..."}, ...]}`
- 메인 개수: `brief["main_colors"]`, 서브 개수: `brief["sub_colors"]`

### `generate_logos(brief, naming, color_palette, image_client, output_dir)` — `logo.py`
- `naming`, `color_palette`는 각각 위 함수들의 반환값입니다 (앞 단계가 실패하면 빈 리스트/빈 dict로 들어올 수 있으니 방어 코드 필요).
- 개수: `brief["logo_concepts_count"]`. 로고 1장 생성 실패가 전체를 막지 않도록 **for 루프 안에서 개별적으로 `ImageGenError`를 잡아 처리**해주세요. (파일 안에 참고용 뼈대 코드가 주석으로 들어있습니다.)
- 반환: 저장에 성공한 파일 경로 리스트 `["output/logo_1.png", ...]`

### `save_palette_image(color_palette, output_dir)` — `palette_image.py`
- `color_palette`는 `generate_color_palette()`의 반환값과 같은 형식 (실패 시 빈 dict 가능).
- `os.path.join(output_dir, "palette.png")`로 저장 권장.
- matplotlib 등 원하는 방식으로 자유롭게 시각화하면 됩니다.

## 브리프(brief) 필드 참고 — `brief.py`가 정규화해서 넘겨주는 값

```python
{
  "topic": str,              # 필수
  "target": str,              # 선택, 없으면 ""
  "keywords": list[str],       # 선택, 없으면 []
  "tone": str,                  # 선택, 없으면 ""
  "naming_count": int,           # 기본값 4
  "slogan_count": int,             # 기본값 3
  "story_length": int,              # 기본값 300
  "main_colors": int,                # 기본값 1
  "sub_colors": int,                   # 기본값 3
  "logo_concepts_count": int,           # 기본값 3
}
```
선택 필드가 빈 값(`""`, `[]`)일 때 프롬프트에서 "미지정 → 알아서 추론" 식으로 안내하는 걸 권장합니다. (`naming.py` 등 다른 예시 참고)

## 에러 처리 원칙

- 각 단계 함수 안에서 실패를 직접 처리하려고 하지 마세요. **그냥 예외가 나면 나는 대로 두면 됩니다.**
- `main.py`의 `run_step()`이 모든 단계를 감싸서, 어떤 단계가 왜 실패했는지 출력하고 다음 단계로 자동으로 넘어갑니다.
- 예외: `logo.py`처럼 한 함수 안에서 여러 번(2~3개) 호출하는 경우는, 하나 실패해도 나머지는 계속 시도하도록 **함수 내부에서 개별 try/except**를 써주세요.

## 테스트 팁

각자 맡은 함수만 독립적으로 테스트하고 싶다면:
```python
from brief import load_brief
from llm_client import LLMClient

brief = load_brief("brief_example.json")
llm_client = LLMClient()

from generators.naming import generate_naming
print(generate_naming(brief, llm_client))
```
