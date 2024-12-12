import aiohttp
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class S3Manager:  # 이름은 유지
    def __init__(self):
        self.api_key_name = "X-API-Key"
        self.api_key = os.getenv("API_KEY")  # 환경 변수에서 API_KEY 가져오기
        self.api_url = os.getenv("PROMPT_API_URL")

    async def get_random_prompt(self, genre: str) -> dict:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="API Key is not configured in environment variables.")

        headers = {self.api_key_name: self.api_key}
        params = {"genre": genre}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to fetch prompt: {await response.text()}"
                        )
                    
                    data = await response.json()

                    # 응답 데이터에서 필요한 값 반환
                    return {
                        "file_name": data.get("file_name", "Unknown"),
                        "content": data.get("content", "")
                    }

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error interacting with backend API: {str(e)}")
