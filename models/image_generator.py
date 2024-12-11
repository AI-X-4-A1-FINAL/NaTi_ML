import os
import openai
from dotenv import load_dotenv
import replicate


# 환경 변수 로드
load_dotenv()

# Replicate API 클라이언트 초기화
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_KEY"))


def generate_image_with_api(prompt: str, size: str = "9:16") -> str:

    try:
        output = replicate_client.run(
            "luma/photon-flash",
            input={
                "prompt": prompt,
                "aspect_ratio": size,
                "image_reference_weight": 0.85,
                "style_reference_weight": 0.85
                
            }
        )

        #print("Output:", output)  # 출력
        return str(output)  # 문자열로 반환
    
    except Exception as e:
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {e}")

