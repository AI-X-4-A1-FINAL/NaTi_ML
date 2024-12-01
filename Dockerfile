# 베이스 이미지 설정 (Python 3.12 사용)
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# Docker build에서 환경 변수를 받을 수 있도록 ARG 추가
ARG CORS_ORIGINS
ARG OPENAI_KEY
ARG DOCKERHUB_USERNAME
ARG DOCKERHUB_PASSWORD
ARG AWS_REGION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG BUCKET_NAME
ARG SSH_PRIVATE_KEY

# ARG 값을 ENV로 설정하여 런타임에 사용
ENV CORS_ORIGINS=${CORS_ORIGINS}
ENV OPENAI_KEY=${OPENAI_KEY}
ENV DOCKERHUB_USERNAME=${DOCKERHUB_USERNAME}
ENV DOCKERHUB_PASSWORD=${DOCKERHUB_PASSWORD}
ENV AWS_REGION=${AWS_REGION}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV BUCKET_NAME=${BUCKET_NAME}
ENV SSH_PRIVATE_KEY=${SSH_PRIVATE_KEY}

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import aioboto3; print(f'aioboto3 version: {aioboto3.__version__}')"
RUN python -c "print('All required packages installed successfully')"

# 애플리케이션 코드 복사
COPY . .

# FastAPI 서버 실행 (uvicorn 사용)
EXPOSE 8050
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]
