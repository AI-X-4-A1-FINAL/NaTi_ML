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

    async def get_random_prompt(self, genre: str, bucket_name: Optional[str] = None) -> str:
        bucket_name = bucket_name or self.bucket_name
        async with aioboto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION"),
        ) as s3_client:
            try:
                folder_key = f"{genre}/"
                response = await s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

                if "Contents" not in response:
                    raise HTTPException(status_code=404, detail="No files found in the specified genre folder")

                files = [obj["Key"] for obj in response["Contents"]]
                random_file = random.choice(files)

                file_obj = await s3_client.get_object(Bucket=bucket_name, Key=random_file)
                return (await file_obj["Body"].read()).decode("utf-8")

            except ClientError as e:
                raise HTTPException(status_code=500, detail=f"Error interacting with S3: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
