from config import IMAGE_API_KEY


class ImageGenError(Exception):
    """이미지 생성 과정에서 발생한 오류를 나타낸다."""
    pass


class ImageClient:
    def __init__(self):
        self.api_key = IMAGE_API_KEY
        if not self.api_key:
            print("[경고] 이미지 생성 API 키가 설정되지 않았습니다. 환경 변수 IMAGE_API_KEY를 확인하세요.")
        # TODO: 실제 SDK 클라이언트 초기화
        # from openai import OpenAI
        # self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, save_path):
        """
        prompt로 이미지를 생성해 save_path에 저장한다.
        실패 시 원인을 담은 ImageGenError를 발생시킨다 (호출부에서 잡아서 처리).
        """
        if not self.api_key:
            raise ImageGenError("API 키가 설정되지 않아 호출할 수 없습니다 (IMAGE_API_KEY 확인 필요).")

        try:
            # TODO: 실제 이미지 생성 API 호출부를 여기에 구현 (예: DALL-E 3)
            # response = self.client.images.generate(
            #     model="dall-e-3", prompt=prompt, size="1024x1024", n=1
            # )
            # image_url = response.data[0].url
            # import requests
            # img_data = requests.get(image_url).content
            # with open(save_path, "wb") as f:
            #     f.write(img_data)
            raise NotImplementedError("이미지 생성 API 호출부가 아직 구현되지 않았습니다 (TODO).")
        except Exception as e:
            raise ImageGenError(f"{e}") from e
