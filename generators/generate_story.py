import json
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

# 1. .env 파일 로드
load_dotenv()

def generate_brand_story(brief, brand_result):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

    client = OpenAI(api_key=api_key)

    # brand_result.json의 top_recommendation 데이터 추출
    top_rec = brand_result.get("top_recommendation", {})
    brand_name = top_rec.get("name", "정보 없음")
    slogan = top_rec.get("slogan", "정보 없음")
    reason = top_rec.get("reason", "정보 없음")

    story_prompt = f"""
    당신은 감성적인 브랜드 스토리텔러입니다. 
    제시된 [브랜드 브리프] 정보와 [네이밍 및 슬로건]을 바탕으로 브랜드 스토리를 작성해 주세요.

    [브랜드 브리프]
    - 주제: {brief.get('topic', '정보 없음')}
    - 타겟: {brief.get('target', '정보 없음')}
    - 키워드: {', '.join(brief.get('keywords', []))}
    - 톤앤매너: {brief.get('tone', '정보 없음')}

    [네이밍 및 슬로건]
    - 브랜드명: {brand_name}
    - 슬로건: {slogan}
    - 컨셉 및 선정 이유: {reason}

    [요청 사항]
    - '{brand_name}' 브랜드명과 '{slogan}' 슬로건의 의미 및 컨셉을 자연스럽게 녹여내어 작성해 주세요.
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
        # 1. brief.json 읽기
        with open("brief.json", "r", encoding="utf-8") as f:
            brief_data = json.load(f)

        # 2. brand_result.json 읽기
        with open("brand_result.json", "r", encoding="utf-8") as f:
            brand_result_data = json.load(f)

        # 3. 스토리 생성
        story_result = generate_brand_story(brief_data, brand_result_data)
        
        if story_result and "story" in story_result:
            print("\n=== 브랜드 스토리 생성 결과 ===")
            print(story_result["story"])
            
            # 4. brand_result_data 객체에 'brand_story' 키로 결과 덮어쓰기/추가
            brand_result_data["brand_story"] = story_result["story"]

            # 5. brand_result.json 파일에 최종 업데이트 저장
            with open("brand_result.json", "w", encoding="utf-8") as f:
                json.dump(brand_result_data, f, ensure_ascii=False, indent=2)
                
            print("\n[성공] brand_result.json 파일에 'brand_story' 항목이 성공적으로 업데이트되었습니다.")

    except FileNotFoundError as e:
        print(f"[Error] 필요한 JSON 파일을 찾을 수 없습니다: {e.filename}")
    except json.JSONDecodeError:
        print("[Error] JSON 파일의 형식이 올바르지 않습니다.")