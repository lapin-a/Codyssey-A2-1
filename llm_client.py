import json
from config import OPENAI_API_KEY


class LLMError(Exception):
    """LLM 호출/파싱 과정에서 발생한 오류를 나타낸다."""
    pass


class LLMClient:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            print("[경고] LLM API 키가 설정되지 않았습니다. 환경 변수 OPENAI_API_KEY를 확인하세요.")
        # TODO: 실제 SDK 클라이언트 초기화
        # from openai import OpenAI
        # self.client = OpenAI(api_key=self.api_key)

    def generate_json(self, system_prompt, user_prompt, model="gpt-4o"):
        """
        LLM에게 JSON 형식 응답을 요청하고 파싱해서 dict로 반환한다.
        실패 시 원인을 담은 LLMError를 발생시킨다 (호출부에서 잡아서 처리).
        """
        if not self.api_key:
            raise LLMError("API 키가 설정되지 않아 호출할 수 없습니다 (OPENAI_API_KEY 확인 필요).")

        try:
            # TODO: 실제 API 호출부를 여기에 구현
            # response = self.client.chat.completions.create(
            #     model=model,
            #     response_format={"type": "json_object"},
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_prompt},
            #     ],
            # )
            # text = response.choices[0].message.content
            # return json.loads(text)
            raise NotImplementedError("LLM 호출부가 아직 구현되지 않았습니다 (TODO).")
        except json.JSONDecodeError as e:
            raise LLMError(f"응답을 JSON으로 파싱하지 못했습니다: {e}") from e
        except Exception as e:
            raise LLMError(f"{e}") from e
