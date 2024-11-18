import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import soundfile as sf
import numpy as np

class MusicGenerator:
    def __init__(self):
        print("Loading processor...")
        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        print("Loading model...")
        
        self.model = MusicgenForConditionalGeneration.from_pretrained(
            "facebook/musicgen-small",
            attn_implementation="eager",
            torch_dtype=torch.float32
        )
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded on {self.device}")

    def preprocess_prompt(self, prompt: str) -> str:
        prompt = prompt.replace("\n", " ").strip()
        return prompt

    def generate_music(self, prompt: str, duration: int = 30):
        try:
            prompt = self.preprocess_prompt(prompt)
            print(f"Generating music for prompt: {prompt} with duration: {duration} seconds")

            # 입력 준비 및 유효성 검사
            inputs = self.processor(text=prompt, return_tensors="pt").input_ids
            if inputs is None or inputs.shape[0] == 0:
                raise ValueError("Invalid input tensor")

            inputs = inputs.to(self.device)
            print(f"Input tensor shape: {inputs.shape}")

            # 메모리 초기화 및 동기화
            torch.cuda.empty_cache()
            if torch.cuda.is_available():
                torch.cuda.synchronize()

            # 음악 생성 단계
            with torch.no_grad():
                output = self.model.generate(
                    inputs=inputs,
                    max_new_tokens=duration * 100,
                    do_sample=True,
                    top_p=0.9,
                    temperature=0.7
                )

            print("Music generated successfully")
            audio = output[0].cpu().numpy()
            
            # MusicGen의 기본 샘플링 레이트를 사용
            sampling_rate = 32000  # MusicGen 모델의 기본 샘플링 레이트
            return audio, sampling_rate

        except Exception as e:
            print(f"Error generating music: {e}")
            raise e 


    def save_audio(self, audio, filename="generated_music.wav", sample_rate=32000):
        try:
            audio = np.array(audio, dtype=np.float32)
            if len(audio.shape) == 1:
                audio = audio[np.newaxis, :]
            
            # 오디오 저장
            sf.write(filename, audio.T, sample_rate)
            print(f"Audio saved as {filename} with sample rate {sample_rate}")
        except Exception as e:
            print(f"Error saving audio: {e}")
            raise e
