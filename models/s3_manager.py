import os
import random
from typing import Optional
from fastapi import HTTPException
import aioboto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class S3Manager:
    def __init__(self):
        self.bucket_name = os.getenv("BUCKET_NAME")

    async def get_random_prompt(self, genre: str, bucket_name: Optional[str] = None) -> dict:
        bucket_name = bucket_name or self.bucket_name
        async with aioboto3.Session().client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        ) as s3_client:
            try:
                # 1. S3 객체 목록 가져오기
                response = await s3_client.list_objects_v2(Bucket=bucket_name)
                if "Contents" not in response or not response["Contents"]:
                    raise HTTPException(status_code=404, detail="No files found in the bucket")

                # 2. 태그가 일치하는 객체 필터링
                matching_files = []
                for obj in response["Contents"]:
                    object_key = obj["Key"]

                    # 객체 태그 가져오기
                    try:
                        tag_response = await s3_client.get_object_tagging(
                            Bucket=bucket_name,
                            Key=object_key
                        )
                        tags = tag_response.get("TagSet", [])

                        # 태그가 genre=survival인 객체 필터링
                        if any(tag["Key"] == "genre" and tag["Value"] == genre for tag in tags):
                            matching_files.append(object_key)
                    except ClientError as e:
                        print(f"Error fetching tags for {object_key}: {e}")
                        continue

                if not matching_files:
                    raise HTTPException(status_code=404, detail=f"No files with tag genre={genre} found")

                # 3. 랜덤 파일 선택
                random_file = random.choice(matching_files)

                # 4. 선택한 파일 내용 가져오기
                file_obj = await s3_client.get_object(Bucket=bucket_name, Key=random_file)
                file_content = (await file_obj["Body"].read()).decode("utf-8")

                # 5. 파일 이름과 내용을 함께 반환
                return {
                    "file_name": random_file,
                    "content": file_content
                }

            except ClientError as e:
                raise HTTPException(status_code=500, detail=f"Error interacting with S3: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
