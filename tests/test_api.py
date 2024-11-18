from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_music():
    response = client.post("/api/music/generate", json={"prompt": "calm and relaxing music"})
    assert response.status_code == 200
    assert "file" in response.json()
