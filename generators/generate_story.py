import json
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# 1. .env 파일 로드
load_dotenv()

def generate_brand_story(brief):
    # API 키 유무 체크
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

    client = OpenAI(api_key=api_key)

    story_prompt = f"""
    당신은 감성적인 브랜드 스토리텔러입니다. 
    제시된 [브랜드 브리프] 정보와 [네이밍 및 슬로건]을 바탕으로 브랜드 스토리를 작성해 주세요.

    [브랜드 브리프]
    - 주제: {brief.get('topic', '정보 없음')}
    - 타겟: {brief.get('target', '정보 없음')}
    - 키워드: {', '.join(brief.get('keywords', []))}
    - 톤앤매너: {brief.get('tone', '정보 없음')}

    [네이밍 및 슬로건]
    - 브랜드명: 느루 (뜻: 여유 있게 천천히 한다는 의미의 순우리말)
    - 슬로건: 천천히, 달콤하게.
    - 컨셉: 서두르지 않고 수제 디저트와 공간이 주는 따뜻한 여유를 음미하는 카페

    [요청 사항]
    - 바쁜 일상 속에서 잠시 속도를 늦추고 쉬어가는 따뜻하고 차분한 감성을 전달해 주세요.
    - 띄어쓰기 포함 약 {brief.get('output_requirement', {}).get('story_length', 300)}자 내외로 작성해 주세요.

    [출력 형식]
    반드시 아래 JSON 구조로만 답변해 주세요.
    {{
      "story": "생성된 브랜드 스토리 텍스트"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional brand strategist and storyteller."},
                {"role": "user", "content": story_prompt}
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
        # brief.json 읽기 시도
        with open("brief.json", "r", encoding="utf-8") as f:
            brief_data = json.load(f)

        story_result = generate_brand_story(brief_data)
        
        if story_result:
            print("\n=== 브랜드 스토리 생성 결과 ===")
            print(story_result["story"])
            
            with open("story_result.json", "w", encoding="utf-8") as f:
                json.dump(story_result, f, ensure_ascii=False, indent=2)
            print("\n[성공] story_result.json 저장 완료")

    except FileNotFoundError:
        print("[Error] brief.json 파일을 찾을 수 없습니다. 파일 경로 및 위치를 확인해 주세요.")
    except json.JSONDecodeError:
        print("[Error] brief.json 파일의 JSON 형식이 올바르지 않습니다.")