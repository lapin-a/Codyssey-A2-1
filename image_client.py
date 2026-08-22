import base64
import os

from config import IMAGE_API_KEY


class ImageGenError(Exception):
    """이미지 생성 과정에서 발생한 오류를 나타낸다."""
    pass


class ImageClient:
    def __init__(self):
        self.api_key = IMAGE_API_KEY
        self.client = None
        if not self.api_key:
            print("[경고] 이미지 생성 API 키가 설정되지 않았습니다. 환경 변수 IMAGE_API_KEY를 확인하세요.")
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, save_path):
        """
        prompt로 이미지를 생성해 save_path에 저장한다.
        실패 시 원인을 담은 ImageGenError를 발생시킨다 (호출부에서 잡아서 처리).
        """
        if not self.api_key or self.client is None:
            raise ImageGenError("API 키가 설정되지 않아 호출할 수 없습니다 (IMAGE_API_KEY 확인 필요).")

        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size="1024x1024",
            )
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            save_dir = os.path.dirname(save_path)
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)

            with open(save_path, "wb") as f:
                f.write(image_bytes)
        except Exception as e:
            raise ImageGenError(f"{e}") from e
