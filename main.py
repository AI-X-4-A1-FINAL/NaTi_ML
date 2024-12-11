# main.py

from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from api.routes import image, story
from fastapi.middleware.cors import CORSMiddleware
from core.config import config


app = FastAPI()

# 릴리스 버전관리
__version__ = "0.0.2"

__release_notes__ = """
## 주요 변경 사항
- 변경사항 : API 키 인증 추가
"""

# API 키 설정
API_KEY = config.API_KEY  # config.py에서 설정
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# 라우터 등록 - API 키 인증 적용
@app.get("/health")
async def health_check():
    return {"message": "OK"}

# API 키 인증을 라우터에 적용
def get_authenticated_router(router):
    for route in router.routes:
        if not route.dependencies:
            route.dependencies = []
        route.dependencies.append(Security(get_api_key))
    return router

# 인증이 적용된 라우터 등록
app.include_router(
    get_authenticated_router(image.router),
    prefix="/api/images",
    tags=["Image"]
)
app.include_router(
    get_authenticated_router(story.router),
    prefix="/api/story",
    tags=["Story"]
)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
