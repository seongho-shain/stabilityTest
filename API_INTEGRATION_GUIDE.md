# 🎨 Stability AI API React + FastAPI 통합 가이드

이 가이드는 Stability AI의 이미지 생성 및 제어 API를 React + FastAPI 환경에서 통합하는 방법을 설명합니다.

## 📋 목차
1. [API 개요](#api-개요)
2. [지원 기능](#지원-기능)
3. [필수 파라미터](#필수-파라미터)
4. [백엔드 구현 (FastAPI)](#백엔드-구현-fastapi)
5. [프론트엔드 구현 (React)](#프론트엔드-구현-react)
6. [테스트 방법](#테스트-방법)
7. [문제 해결](#문제-해결)

## 🎯 API 개요

### Base URL
```
https://api.stability.ai
```

### 인증
```
Authorization: Bearer YOUR_API_KEY
```

### 지원되는 엔드포인트

#### 1. 이미지 생성
| 모델 | 엔드포인트 | 설명 | 크레딧 |
|-----|-----------|------|--------|
| **Core** | `/v2beta/stable-image/generate/core` | 기본 텍스트→이미지 | 3 |
| **SD3.5** | `/v2beta/stable-image/generate/sd3` | 고급 이미지 생성 (Text/Image-to-Image) | 3.5-6.5 |
| **Ultra** | `/v2beta/stable-image/generate/ultra` | 최고급 이미지 생성 | 8 |

#### 2. 이미지 제어/편집
| 기능 | 엔드포인트 | 설명 | 크레딧 |
|-----|-----------|------|--------|
| **Sketch** | `/v2beta/stable-image/control/sketch` | 스케치→이미지 | 3 |
| **Structure** | `/v2beta/stable-image/control/structure` | 구조 제어 | 3 |
| **Style Guide** | `/v2beta/stable-image/control/style` | 스타일 참조 | 4 |
| **Style Transfer** | `/v2beta/stable-image/control/style-transfer` | 스타일 전송 | 8 |

## ⚙️ 지원 기능

### 이미지 생성 모드
- **Text-to-Image**: 텍스트 프롬프트만으로 이미지 생성
- **Image-to-Image**: 입력 이미지 + 텍스트로 이미지 변형 (SD3.5, Ultra)

### 제어 가능한 속성 (요청사항에 따라 4가지만)
1. **출력 형식**: `png`, `jpeg`, `webp`
2. **이미지 비율**: `1:1`, `16:9`, `9:16`, `3:2`, `2:3`, `4:3`, `3:4`
3. **스타일 프리셋**: `photographic`, `anime`, `digital-art`, `3d-model`, `pixel-art`, `cinematic`, `fantasy-art`, `illustration`
4. **시드**: 랜덤 생성 제어 (0 = 랜덤)

## 📝 필수 파라미터

### 공통 필수 파라미터
```javascript
{
  "prompt": "string (최대 10,000자)"
}
```

### 모델별 추가 파라미터

#### SD3.5 (Image-to-Image 모드)
```javascript
{
  "mode": "image-to-image",
  "image": "binary file",
  "strength": 0.8  // 0.0-1.0
}
```

#### Ultra (참조 이미지 사용)
```javascript
{
  "image": "binary file",
  "strength": 0.5  // 0.0-1.0
}
```

#### 제어 API (Sketch, Structure, Style Guide)
```javascript
{
  "image": "binary file",
  "control_strength": 0.7  // 0.0-1.0
}
```

#### Style Transfer
```javascript
{
  "init_image": "binary file",
  "style_image": "binary file",
  "style_strength": 1.0,     // 0.0-1.0
  "composition_fidelity": 0.9, // 0.0-1.0
  "change_strength": 0.9      // 0.1-1.0
}
```

## 🖥️ 백엔드 구현 (FastAPI)

### 프로젝트 구조
```
backend/
├── main.py                 # FastAPI 앱
├── models/
│   ├── __init__.py
│   └── schemas.py          # Pydantic 스키마
├── services/
│   ├── __init__.py
│   └── stability_client.py # API 클라이언트
├── routers/
│   ├── __init__.py
│   └── image_generation.py # 라우터
└── requirements.txt
```

### 의존성 (requirements.txt)
```
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.0.0
pydantic>=2.4.0
```

### 환경 변수 (.env)
```
STABILITY_API_KEY=your_api_key_here
DEBUG=True
```

## ⚛️ 프론트엔드 구현 (React)

### 필요한 패키지
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.47.0",
    "@mui/material": "^5.14.0"  // 선택사항
  }
}
```

### 컴포넌트 구조
```
src/
├── components/
│   ├── ImageGeneration/
│   │   ├── ImageGenerationForm.jsx
│   │   ├── ModelSelector.jsx
│   │   └── ParameterControls.jsx
│   ├── ImageControl/
│   │   ├── ImageControlForm.jsx
│   │   └── FileUpload.jsx
│   └── common/
│       ├── LoadingSpinner.jsx
│       └── ErrorDisplay.jsx
├── services/
│   └── stabilityApi.js     # API 호출 함수
├── utils/
│   └── validation.js       # 파일 검증
└── hooks/
    └── useImageGeneration.js
```

## 🧪 테스트 방법

### 1. Postman/curl 테스트

#### 텍스트→이미지 (Core)
```bash
curl -X POST "http://localhost:8000/api/image/generate/core" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "output_format": "png",
    "aspect_ratio": "16:9",
    "style_preset": "photographic",
    "seed": 12345
  }'
```

#### 이미지→이미지 (SD3.5)
```bash
curl -X POST "http://localhost:8000/api/image/generate/sd35" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=Transform this into a painting" \
  -F "mode=image-to-image" \
  -F "image=@input.jpg" \
  -F "strength=0.8" \
  -F "output_format=png"
```

### 2. React 컴포넌트 테스트
```javascript
// 기본 텍스트→이미지 테스트
const testData = {
  prompt: "A cute cat wearing a hat",
  output_format: "png",
  aspect_ratio: "1:1",
  style_preset: "anime",
  seed: 0
};

// API 호출
const result = await generateImage('core', testData);
```

## 🔧 문제 해결

### 일반적인 오류들

#### 1. 인증 오류 (401)
```json
{
  "error": "Invalid API key"
}
```
**해결방법**: `.env` 파일의 API 키 확인

#### 2. 파일 크기 오류 (413)
```json
{
  "error": "File too large"
}
```
**해결방법**: 이미지 크기를 50MB 이하로 조정

#### 3. 파라미터 오류 (400)
```json
{
  "error": "Missing required parameter: image"
}
```
**해결방법**: Image-to-Image 모드에서 이미지 파일 확인

### 파일 검증 규칙
- **지원 형식**: JPEG, PNG, WebP
- **최대 크기**: 50MB
- **최소 해상도**: 64x64px
- **최대 픽셀**: 9,437,184 (약 3072x3072)
- **종횡비**: 1:2.5 ~ 2.5:1

### 성능 최적화 팁
1. **이미지 압축**: 업로드 전 이미지 최적화
2. **로딩 상태**: 사용자에게 진행 상황 표시
3. **에러 재시도**: 네트워크 오류 시 재시도 로직
4. **캐싱**: 생성된 이미지 결과 캐싱

## 📚 추가 리소스

- [Stability AI 공식 문서](https://platform.stability.ai/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)

## 🔗 예제 파일들

이 가이드와 함께 제공되는 예제 파일들:
- `fastapi_backend_example.py` - 완전한 FastAPI 백엔드
- `react_frontend_example.js` - React 컴포넌트 예제
- `api_schemas.py` - Pydantic 스키마 정의
- `stability_client.py` - 순수 Python API 클라이언트
- `test_examples.md` - 상세한 테스트 예제