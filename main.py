from fastapi import FastAPI
from api.routes import image, story
from fastapi.middleware.cors import CORSMiddleware
from core.config import config

app = FastAPI()

# 릴리스 버전관리
__version__ = "0.0.2"

__release_notes__ = """
## 주요 변경 사항
- 변경사항 : 
"""

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(image.router, prefix="/api/images", tags=["Image"])
app.include_router(story.router, prefix="/api/story", tags=["Story"])

@app.get("/health")
async def health_check():
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)