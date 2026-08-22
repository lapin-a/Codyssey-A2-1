import json
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# 1. .env 파일 로드
load_dotenv()

def generate_color_recommendations(brief, brand_result):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

    client = OpenAI(api_key=api_key)

    # brand_result.json의 top_recommendation 데이터 추출
    top_rec = brand_result.get("top_recommendation", {})
    brand_name = top_rec.get("name", "정보 없음")
    slogan = top_rec.get("slogan", "정보 없음")
    reason = top_rec.get("reason", "정보 없음")

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
    - 브랜드명: {brand_name}
    - 슬로건: {slogan}
    - 컨셉 및 선정 이유: {reason}

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
        # 1. brief.json 읽기
        with open("brief.json", "r", encoding="utf-8") as f:
            brief_data = json.load(f)

        # 2. brand_result.json 읽기
        with open("brand_result.json", "r", encoding="utf-8") as f:
            brand_result_data = json.load(f)

        # 3. 컬러 추천 결과 생성
        color_result = generate_color_recommendations(brief_data, brand_result_data)
        
        if color_result and "color_palette" in color_result:
            print("\n=== 컬러 추천 결과 ===")
            print(json.dumps(color_result, ensure_ascii=False, indent=2))
            
            # 4. brand_result_data 객체에 'color_palette' 키로 저장
            brand_result_data["color_palette"] = color_result["color_palette"]

            # 5. brand_result.json 파일에 최종 업데이트 저장
            with open("brand_result.json", "w", encoding="utf-8") as f:
                json.dump(brand_result_data, f, ensure_ascii=False, indent=2)
                
            print("\n[성공] brand_result.json 파일에 'color_palette' 항목이 성공적으로 업데이트되었습니다.")

    except FileNotFoundError as e:
        print(f"[Error] 필요한 JSON 파일을 찾을 수 없습니다: {e.filename}")
    except json.JSONDecodeError:
        print("[Error] JSON 파일의 형식이 올바르지 않습니다.")