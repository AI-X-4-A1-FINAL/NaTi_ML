from pydantic import BaseModel

class ImageRequest(BaseModel):
    gameId: int
    stageNumber: int
    prompt: str  # 사용자가 입력할 프롬프트
    size: str = "256x256"  # 이미지 크기 (기본값 제공)
    n: int = 1  # 생성할 이미지 수 (기본값 제공)
    genre: str  # 이미지 장르