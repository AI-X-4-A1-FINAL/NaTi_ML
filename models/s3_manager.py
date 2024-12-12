import aiohttp
import os
import logging
from fastapi import HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)

class PromptResponse(BaseModel):
    file_name: str
    content: str

class S3Manager:
    def __init__(self):
        self.api_key_name = "X-API-Key"
        self.api_key = os.getenv("API_KEY", "default_api_key")
        self.api_url = os.getenv("PROMPT_API_URL", "http://default-url.com")

        if not self.api_key:
            raise ValueError("API Key is missing. Check your environment variables.")
        if not isinstance(self.api_url, str) or not self.api_url.startswith("http"):
            raise ValueError("API URL must be a valid string starting with 'http'.")

    async def get_random_prompt(self, genre: str) -> dict:
        if not genre or not isinstance(genre, str):
            raise ValueError("Genre must be a non-empty string.")

        headers = {self.api_key_name: self.api_key}
        params = {"genre": genre}

        logging.info(f"Fetching prompt for genre: {genre}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logging.error(f"API returned error: {response.status}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to fetch prompt: {await response.text()}"
                        )
                    
                    response_data = await response.json()
                    validated_data = PromptResponse(**response_data)

                    logging.info(f"Prompt fetched successfully for genre: {genre}")
                    return validated_data.dict()

            except ValueError as ve:
                logging.error(f"Value error in backend API interaction: {str(ve)}")
                raise HTTPException(status_code=500, detail=f"Value error: {str(ve)}")
            except Exception as e:
                logging.error(f"Error interacting with backend API: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Backend API error: {str(e)}")
