#models/s3_manager.py

import aiohttp
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class S3Manager:
    def __init__(self): 
        self.api_key_name = "X-API-Key"
        self.api_key = os.getenv("API_KEY")
        self.api_url = os.getenv("BACK_BASE_URL")

        if not self.api_key:
            raise ValueError("API Key is missing. Check your environment variables.")
        if not isinstance(self.api_url, str) or not self.api_url.startswith("http"):
            raise ValueError("API URL must be a valid string starting with 'http'.")

    async def get_random_prompt(self, genre: str) -> dict:
        """랜덤 프롬프트 가져오기"""
        if not genre or not isinstance(genre, str):
            raise ValueError("Genre must be a non-empty string.")

        headers = {self.api_key_name: self.api_key}
        url = f"{self.api_url}/api/prompts/random"
        params = {"genre": genre}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to fetch prompt: {await response.text()}"
                        )
                    
                    try:
                        data = await response.json()
                    except Exception as json_error:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to parse JSON response: {str(json_error)}"
                        )

                    return {
                        "file_name": data.get("file_name", "Unknown"),
                        "content": data.get("content", "")
                    }

            except ValueError as ve:
                raise HTTPException(status_code=500, detail=f"Value error in backend API interaction: {str(ve)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error interacting with backend API: {str(e)}")
    
    async def get_genre_type_template(self, genre: str, template_type: str) -> dict:
        """백엔드에서 특정 장르와 타입의 템플릿 가져오기"""
        if not genre or not template_type:
            raise ValueError("Genre and template_type must be non-empty strings.")

        url = f"{self.api_url}/api/templates/{genre}/{template_type}"
        headers = {self.api_key_name: self.api_key}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to fetch template: {await response.text()}"
                        )
                    
                    try:
                        return await response.json()
                    except Exception as json_error:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to parse JSON response: {str(json_error)}"
                        )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching template: {str(e)}")