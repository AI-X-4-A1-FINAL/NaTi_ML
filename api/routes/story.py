from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
import random
import os
from typing import List
from dotenv import load_dotenv
from models.story_generator import generate_story
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError

load_dotenv()

router = APIRouter()

# S3 클라이언트 설정
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# S3에서 프롬프트 가져오기
def get_random_prompt_from_s3(genre: str, bucket_name: str = None) -> str:
    bucket_name = bucket_name or os.getenv("BUCKET_NAME")
    try:
        folder_key = f"{genre}/"  # 예: "Survival/" 또는 "Romance/"

        # S3에서 객체 목록 가져오기
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

        if 'Contents' not in response:
            raise HTTPException(status_code=404, detail="No files found in the specified genre folder")

        # 파일 목록에서 랜덤으로 하나 선택
        files = [obj['Key'] for obj in response['Contents']]
        random_file = random.choice(files)

        # 선택된 파일 읽기
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=random_file)
        file_content = file_obj['Body'].read().decode('utf-8')

        return file_content

    except ClientError as e:  # boto3에서 발생할 수 있는 예외를 잡기
        raise HTTPException(status_code=500, detail=f"Error interacting with S3: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# 요청 모델 정의
class StoryRequest(BaseModel):
    genre: str
    tags: List[str]

# 초기 스토리 생성 엔드포인트
@router.post("/start")
def generate_story_endpoint(request: StoryRequest):
    try:
        # S3에서 프롬프트 파일 가져오기
        prompt = get_random_prompt_from_s3(request.genre)
        
        # tags와 프롬프트를 결합하여 스토리 생성에 사용
        modified_prompt = f"{prompt}\n\nTags: {', '.join(request.tags)}"

        # 스토리 생성
        response = generate_story(request.genre, modified_prompt)
        return {"story": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")
