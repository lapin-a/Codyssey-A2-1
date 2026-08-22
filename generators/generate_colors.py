import json
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# 1. .env 파일 로드
load_dotenv()

def generate_color_recommendations(brief):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

    client = OpenAI(api_key=api_key)

    req_palette = brief.get('output_requirement', {}).get('color_palette', {})
    main_count = req_palette.get('main_colors', 1)
    sub_count = req_palette.get('sub_colors', 3)

    color_prompt = f"""
    당신은 브랜딩 전문 컬러 디렉터입니다. 
    제시된 [브랜드 브리프] 정보와 [네이밍 및 분위기]에 어울리는 컬러(HEX 코드)를 추천해 주세요.

    [브랜드 브리프]
    - 주제: {brief.get('topic', '정보 없음')}
    - 타겟: {brief.get('target', '정보 없음')}
    - 키워드: {', '.join(brief.get('keywords', []))}
    - 톤앤매너: {brief.get('tone', '정보 없음')}

    [네이밍 및 분위기]
    - 브랜드명: 느루 (슬로건: 천천히, 달콤하게.)
    - 분위기: 따뜻함, 느긋함, 수제 디저트의 감성, 조용하고 포근한 공간

    [요청 사항]
    - 차분하고 아늑한 수제 카페 콘셉트에 어울리는 HEX 코드를 추천해 주세요.
    - 메인 컬러 {main_count}개, 서브 컬러 {sub_count}개를 추천해 주세요.

    [출력 형식]
    반드시 아래 JSON 구조로만 답변해 주세요.
    {{
      "color_palette": {{
        "main": {{
          "hex": "#HEX코드",
          "name": "색상명",
          "reason": "추천 이유"
        }},
        "sub": [
          {{
            "hex": "#HEX코드1",
            "name": "색상명1",
            "reason": "추천 이유1"
          }},
          {{
            "hex": "#HEX코드2",
            "name": "색상명2",
            "reason": "추천 이유2"
          }},
          {{
            "hex": "#HEX코드3",
            "name": "색상명3",
            "reason": "추천 이유3"
          }}
        ]
      }}
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional brand color director."},
                {"role": "user", "content": color_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    except AuthenticationError:
        print("[Error] OpenAI API 키가 올바르지 않습니다. .env 파일의 Key 값을 재확인하세요.")
    except APIError as e:
        print(f"[Error] OpenAI API 통신 중 오류가 발생했습니다: {e}")
    except json.JSONDecodeError:
        print("[Error] LLM 답변을 JSON으로 파싱하는 데 실패했습니다.")
    except Exception as e:
        print(f"[Error] 알 수 없는 오류 발생: {e}")

    return None

if __name__ == "__main__":
    try:
        with open("brief.json", "r", encoding="utf-8") as f:
            brief_data = json.load(f)

        color_result = generate_color_recommendations(brief_data)
        
        if color_result:
            print("\n=== 컬러 추천 결과 ===")
            print(json.dumps(color_result, ensure_ascii=False, indent=2))
            
            with open("color_result.json", "w", encoding="utf-8") as f:
                json.dump(color_result, f, ensure_ascii=False, indent=2)
            print("\n[성공] color_result.json 저장 완료")

    except FileNotFoundError:
        print("[Error] brief.json 파일을 찾을 수 없습니다. 파일 경로 및 위치를 확인해 주세요.")
    except json.JSONDecodeError:
        print("[Error] brief.json 파일의 JSON 형식이 올바르지 않습니다.")