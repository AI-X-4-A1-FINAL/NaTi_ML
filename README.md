![NARRATIVA-TITLE](https://github.com/user-attachments/assets/97538156-f202-4b48-8543-9bbf835fda0e)

# Narrativa ML

![Python](https://img.shields.io/badge/Python-v3.12.7-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-v2.5.1-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.115.4-009688?style=for-the-badge&logo=fastapi&logoColor=white)

## 🗝️ 프로젝트 소개

`Narrativa_ML`은 AI 기반 스토리 생성 플랫폼인 Narrativa 프로젝트의 AI API 모듈입니다.<br />


## 🗝️ 설치 가이드

Narrativa_ML 프로젝트를 로컬 환경에서 클론하고, 빌드 및 실행하는 방법을 설명합니다.

### 1. 프로젝트 클론
```bash
git clone https://github.com/AI-X-4-A1-FINAL/Narrativa_ML.git
cd narrativa-ml
```

### 2. 빌드 및 설치
```bash
코드추가 예정
```

### 3. 실행
```bash
코드추가 예정
```

## 🗝️ 브랜치 관리 규칙

### 브랜치 구조
1. **메인 브랜치 (main)**
    - 프로덕션 배포용 안정 브랜치
    - PR을 통해서만 병합 가능

2. **개발 브랜치 (dev)**
    - 개발 중인 기능 통합 브랜치
    - 배포 전 최종 테스트 진행

3. **기능 브랜치 (feat/)**
    - 새로운 기능 개발용
    - 명명규칙: `feat/{기능명}`
    - 예: `feat/social-login`

4. **긴급 수정 브랜치 (hotfix/)**
    - 프로덕션 긴급 버그 수정용
    - 명명규칙: `hotfix/{이슈번호}`
    - 예: `hotfix/critical-bug`

### 브랜치 사용 예시
```bash
# 기능 브랜치 생성
git checkout -b feat/social-login

# 긴급 수정 브랜치 생성
git checkout -b hotfix/critical-bug
```

## 🗝️ API 설계 규칙

### RESTful API 표준

#### HTTP 메서드
- `GET`: 데이터 조회
- `POST`: 데이터 생성
- `PUT`: 데이터 수정
- `DELETE`: 데이터 삭제

#### 상태 코드
- `200`: 요청 성공
- `201`: 생성 성공
- `204`: 성공 (응답 데이터 없음)
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `409`: 데이터 충돌
- `500`: 서버 오류

### 엔드포인트 규칙
- 소문자 및 케밥 케이스 사용
- 복수형 리소스 명사 사용
- 예시:
    - `/users/{userId}`
    - `/games/{gameId}/sessions`

### 파라미터 규칙
- 쿼리: 카멜 케이스
    - `?startDate=2024-11-14`
- 경로: 케밥 케이스
    - `/users/{user-id}`

## 🗝️ 디렉토리 구조

```bash
구조추가
```

## 🗝️ 팀 정보

### **Team Member**
  <br />
  <img src="https://github.com/user-attachments/assets/bb285012-1e08-4bd7-9c63-d6f73c80f713" 
       alt="st" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
  <img src="https://github.com/user-attachments/assets/6e4a6035-db22-414a-b051-b59fd646d9cd" 
       alt="hs" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
  <img src="https://github.com/user-attachments/assets/b07709bc-bd82-4401-a5cd-9177e4ee44e6" 
       alt="hy" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
  <img src="https://github.com/user-attachments/assets/6a1bbf66-b4d6-40b2-afc9-113e37d78884" 
       alt="js" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
<a href="https://github.com/shaneee123" target="_blank">
  <img src="https://github.com/user-attachments/assets/6ec7ec21-a9b1-4ebe-932f-c78064dcabe7" 
       alt="se" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
</a>
<a href="https://github.com/Yesssung" target="_blank">
  <img src="https://github.com/user-attachments/assets/2ce88918-3e99-4dba-97c1-ef54d0cd4d48" 
       alt="ys" 
       width="200" 
       height="auto" 
       style="max-width: 100%; height: auto;">
</a>

## 🗝️ 문의 및 기여

프로젝트에 대한 문의사항이나 개선 제안은 이슈 탭에 등록해주세요.<br />
기여를 원하시는 분은 Fork & Pull Request를 통해 참여해주시면 감사하겠습니다.


<br /><br />
![footer](https://github.com/user-attachments/assets/c30abbd9-8e89-4a4e-8823-33fe0cf843c9)
