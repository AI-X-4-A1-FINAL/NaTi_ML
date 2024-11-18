from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.music_generator import MusicGenerator

router = APIRouter()
music_generator = MusicGenerator()

class MusicRequest(BaseModel):
    prompt: str
    duration: int = 15

@router.post("/generate", summary="Generate music from text")
async def generate_music(request: MusicRequest):
    try:
        audio, sample_rate = music_generator.generate_music(request.prompt, request.duration)
        filename = "generated_music.wav"
        music_generator.save_audio(audio, filename, sample_rate)
        return {"message": "Music generated successfully!", "filename": filename}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
