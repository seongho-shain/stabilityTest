# 🧪 Stability AI API 테스트 가이드 및 예제

이 문서는 Stability AI API를 React + FastAPI 환경에서 테스트하는 방법을 설명합니다.

## 📋 목차
1. [환경 설정](#환경-설정)
2. [백엔드 테스트](#백엔드-테스트)
3. [프론트엔드 테스트](#프론트엔드-테스트)
4. [API 테스트 도구](#api-테스트-도구)
5. [문제 해결](#문제-해결)

## 🔧 환경 설정

### 1. 백엔드 설정 (FastAPI)

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install fastapi uvicorn python-multipart requests python-dotenv Pillow pydantic

# 환경변수 설정
echo "STABILITY_API_KEY=your-api-key-here" > .env

# 서버 실행
python fastapi_backend_example.py
```

### 2. 프론트엔드 설정 (React)

```bash
# React 앱 생성
npx create-react-app stability-frontend
cd stability-frontend

# 의존성 설치
npm install axios

# 환경변수 설정
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# 개발 서버 실행
npm start
```

## 🖥️ 백엔드 테스트

### 1. 헬스체크 테스트

```bash
curl -X GET "http://localhost:8000/health"
```

**예상 응답:**
```json
{
  "status": "healthy",
  "api_available": true,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. Stable Image Core 테스트

```bash
curl -X POST "http://localhost:8000/api/image/generate/core" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "output_format": "png",
    "aspect_ratio": "16:9",
    "style_preset": "photographic",
    "seed": 12345
  }' \
  --output "test_core.png"
```

### 3. Stable Diffusion 3.5 (Text-to-Image) 테스트

```bash
curl -X POST "http://localhost:8000/api/image/generate/sd35" \
  -F "prompt=A futuristic city at night" \
  -F "mode=text-to-image" \
  -F "model=sd3.5-large" \
  -F "aspect_ratio=16:9" \
  -F "output_format=png" \
  -F "style_preset=digital-art" \
  --output "test_sd35_t2i.png"
```

### 4. Stable Diffusion 3.5 (Image-to-Image) 테스트

```bash
curl -X POST "http://localhost:8000/api/image/generate/sd35" \
  -F "prompt=Transform this into a painting" \
  -F "mode=image-to-image" \
  -F "model=sd3.5-large" \
  -F "strength=0.8" \
  -F "output_format=png" \
  -F "style_preset=digital-art" \
  -F "image=@input_image.jpg" \
  --output "test_sd35_i2i.png"
```

### 5. Stable Image Ultra 테스트

```bash
curl -X POST "http://localhost:8000/api/image/generate/ultra" \
  -F "prompt=A professional portrait photo" \
  -F "aspect_ratio=3:4" \
  -F "output_format=jpeg" \
  -F "style_preset=photographic" \
  --output "test_ultra.jpg"
```

### 6. 이미지 제어 테스트

#### Sketch ControlNet
```bash
curl -X POST "http://localhost:8000/api/image/control/sketch" \
  -F "prompt=A detailed castle on a hill" \
  -F "control_strength=0.7" \
  -F "output_format=png" \
  -F "style_preset=fantasy-art" \
  -F "image=@sketch.png" \
  --output "test_sketch.png"
```

#### Structure ControlNet
```bash
curl -X POST "http://localhost:8000/api/image/control/structure" \
  -F "prompt=A modern building" \
  -F "control_strength=0.7" \
  -F "output_format=png" \
  -F "image=@structure_ref.png" \
  --output "test_structure.png"
```

#### Style Guide ControlNet
```bash
curl -X POST "http://localhost:8000/api/image/control/style-guide" \
  -F "prompt=A beautiful landscape" \
  -F "fidelity=0.5" \
  -F "aspect_ratio=16:9" \
  -F "output_format=png" \
  -F "image=@style_ref.png" \
  --output "test_style_guide.png"
```

#### Style Transfer
```bash
curl -X POST "http://localhost:8000/api/image/control/style-transfer" \
  -F "style_strength=1.0" \
  -F "composition_fidelity=0.9" \
  -F "change_strength=0.9" \
  -F "output_format=png" \
  -F "init_image=@original.png" \
  -F "style_image=@style.png" \
  --output "test_style_transfer.png"
```

## ⚛️ 프론트엔드 테스트

### 1. 컴포넌트 단위 테스트

```javascript
// components/ImageGeneration.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ImageGenerationApp from './ImageGenerationApp';

test('프롬프트 입력 및 이미지 생성', async () => {
  render(<ImageGenerationApp />);
  
  // 프롬프트 입력
  const promptInput = screen.getByPlaceholderText(/생성하고 싶은 이미지/);
  fireEvent.change(promptInput, { target: { value: 'A beautiful sunset' } });
  
  // 생성 버튼 클릭
  const generateButton = screen.getByText('🎨 이미지 생성');
  fireEvent.click(generateButton);
  
  // 로딩 상태 확인
  expect(screen.getByText('생성 중...')).toBeInTheDocument();
  
  // 결과 확인 (API 모킹 필요)
  await waitFor(() => {
    expect(screen.getByText('생성된 이미지')).toBeInTheDocument();
  });
});
```

### 2. API 호출 테스트

```javascript
// services/api.test.js
import axios from 'axios';
import { generateCoreImage, generateSD35Image } from './stabilityApi';

jest.mock('axios');
const mockedAxios = axios;

test('Core 이미지 생성 API 호출', async () => {
  const mockResponse = { data: new Blob() };
  mockedAxios.post.mockResolvedValue(mockResponse);
  
  const formData = {
    prompt: 'Test prompt',
    output_format: 'png',
    aspect_ratio: '1:1'
  };
  
  const result = await generateCoreImage(formData);
  
  expect(mockedAxios.post).toHaveBeenCalledWith(
    '/api/image/generate/core',
    expect.any(FormData),
    expect.any(Object)
  );
  expect(result).toBe(mockResponse);
});
```

### 3. 파일 업로드 테스트

```javascript
// utils/fileValidation.test.js
import { validateImageFile } from './validation';

test('이미지 파일 검증 - 유효한 파일', () => {
  const validFile = new File([''], 'test.png', { type: 'image/png' });
  const result = validateImageFile(validFile);
  
  expect(result.valid).toBe(true);
});

test('이미지 파일 검증 - 무효한 파일 형식', () => {
  const invalidFile = new File([''], 'test.txt', { type: 'text/plain' });
  const result = validateImageFile(invalidFile);
  
  expect(result.valid).toBe(false);
  expect(result.error).toContain('지원되지 않는 파일 형식');
});
```

## 🛠️ API 테스트 도구

### 1. Postman 컬렉션

```json
{
  "info": {
    "name": "Stability AI API Tests",
    "description": "React + FastAPI 백엔드 테스트"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{baseUrl}}/health"
      }
    },
    {
      "name": "Generate Core Image",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"prompt\": \"A beautiful sunset over mountains\",\n  \"output_format\": \"png\",\n  \"aspect_ratio\": \"16:9\",\n  \"style_preset\": \"photographic\"\n}"
        },
        "url": "{{baseUrl}}/api/image/generate/core"
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    }
  ]
}
```

### 2. Python 테스트 스크립트

```python
# test_api.py
import requests
import time
import os

API_BASE = "http://localhost:8000"

def test_health():
    """헬스체크 테스트"""
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ 헬스체크 통과")

def test_core_generation():
    """Core 이미지 생성 테스트"""
    data = {
        "prompt": "A beautiful sunset over mountains",
        "output_format": "png",
        "aspect_ratio": "16:9",
        "style_preset": "photographic"
    }
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/image/generate/core", json=data)
    end_time = time.time()
    
    assert response.status_code == 200
    assert response.headers.get('content-type').startswith('image/')
    
    # 파일 저장
    with open("test_core_output.png", "wb") as f:
        f.write(response.content)
    
    print(f"✅ Core 이미지 생성 완료 ({end_time - start_time:.2f}초)")

def test_sd35_text_to_image():
    """SD3.5 텍스트→이미지 테스트"""
    data = {
        "prompt": "A futuristic city at night",
        "mode": "text-to-image",
        "model": "sd3.5-large",
        "aspect_ratio": "16:9",
        "output_format": "png"
    }
    
    response = requests.post(f"{API_BASE}/api/image/generate/sd35", data=data)
    assert response.status_code == 200
    
    with open("test_sd35_t2i.png", "wb") as f:
        f.write(response.content)
    
    print("✅ SD3.5 텍스트→이미지 생성 완료")

def test_image_upload():
    """이미지 업로드 테스트"""
    # 테스트 이미지가 있다고 가정
    if not os.path.exists("test_input.jpg"):
        print("⚠️ test_input.jpg 파일이 없어서 이미지 업로드 테스트를 건너뜁니다")
        return
    
    files = {"image": open("test_input.jpg", "rb")}
    data = {
        "prompt": "Transform this into a painting",
        "mode": "image-to-image",
        "model": "sd3.5-large",
        "strength": 0.8,
        "output_format": "png"
    }
    
    response = requests.post(f"{API_BASE}/api/image/generate/sd35", data=data, files=files)
    assert response.status_code == 200
    
    with open("test_sd35_i2i.png", "wb") as f:
        f.write(response.content)
    
    print("✅ SD3.5 이미지→이미지 생성 완료")

if __name__ == "__main__":
    print("🧪 API 테스트 시작...")
    
    try:
        test_health()
        test_core_generation()
        test_sd35_text_to_image()
        test_image_upload()
        print("\n🎉 모든 테스트 통과!")
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
```

### 3. JavaScript 테스트 스크립트

```javascript
// test_api.js (Node.js)
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const API_BASE = 'http://localhost:8000';

async function testHealth() {
  try {
    const response = await axios.get(`${API_BASE}/health`);
    console.log('✅ 헬스체크 통과:', response.data);
  } catch (error) {
    console.error('❌ 헬스체크 실패:', error.message);
  }
}

async function testCoreGeneration() {
  try {
    const data = {
      prompt: 'A beautiful sunset over mountains',
      output_format: 'png',
      aspect_ratio: '16:9',
      style_preset: 'photographic'
    };
    
    const response = await axios.post(`${API_BASE}/api/image/generate/core`, data, {
      responseType: 'stream'
    });
    
    const writer = fs.createWriteStream('test_core_js.png');
    response.data.pipe(writer);
    
    writer.on('finish', () => {
      console.log('✅ Core 이미지 생성 완료');
    });
  } catch (error) {
    console.error('❌ Core 이미지 생성 실패:', error.message);
  }
}

async function testImageUpload() {
  try {
    if (!fs.existsSync('test_input.jpg')) {
      console.log('⚠️ test_input.jpg 파일이 없어서 이미지 업로드 테스트를 건너뜁니다');
      return;
    }
    
    const form = new FormData();
    form.append('prompt', 'Transform this into a painting');
    form.append('mode', 'image-to-image');
    form.append('model', 'sd3.5-large');
    form.append('strength', '0.8');
    form.append('output_format', 'png');
    form.append('image', fs.createReadStream('test_input.jpg'));
    
    const response = await axios.post(`${API_BASE}/api/image/generate/sd35`, form, {
      headers: form.getHeaders(),
      responseType: 'stream'
    });
    
    const writer = fs.createWriteStream('test_sd35_i2i_js.png');
    response.data.pipe(writer);
    
    writer.on('finish', () => {
      console.log('✅ SD3.5 이미지→이미지 생성 완료');
    });
  } catch (error) {
    console.error('❌ 이미지 업로드 테스트 실패:', error.message);
  }
}

async function runTests() {
  console.log('🧪 JavaScript API 테스트 시작...');
  
  await testHealth();
  await testCoreGeneration();
  await testImageUpload();
  
  console.log('\n🎉 JavaScript 테스트 완료!');
}

runTests();
```

## 🔧 문제 해결

### 일반적인 오류들

#### 1. CORS 오류 (프론트엔드에서)
```
Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**해결방법:**
```python
# FastAPI에서 CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 URL 추가
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. API 키 오류
```json
{"detail": "STABILITY_API_KEY 환경변수가 설정되지 않았습니다"}
```

**해결방법:**
```bash
# .env 파일 확인
cat .env
# STABILITY_API_KEY=your-actual-api-key

# 환경변수 로드 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('STABILITY_API_KEY'))"
```

#### 3. 파일 업로드 오류
```json
{"detail": "지원되지 않는 파일 형식입니다"}
```

**해결방법:**
- 파일 형식 확인: JPEG, PNG, WebP만 지원
- 파일 크기 확인: 최대 50MB
- MIME 타입 확인: Content-Type 헤더

#### 4. 타임아웃 오류
```
TimeoutError: Request timed out
```

**해결방법:**
```javascript
// 프론트엔드에서 타임아웃 증가
const api = axios.create({
  timeout: 120000, // 2분으로 증가
});
```

```python
# 백엔드에서 타임아웃 증가
response = await client.generate_image(..., timeout=120)
```

### 성능 최적화 팁

1. **이미지 압축**: 업로드 전 이미지 크기 최적화
2. **병렬 처리**: 여러 요청을 동시에 처리
3. **캐싱**: 동일한 요청 결과 캐싱
4. **스트리밍**: 큰 파일은 스트리밍으로 전송

### 디버깅 팁

1. **로그 확인**: FastAPI 서버 로그 모니터링
2. **네트워크 탭**: 브라우저 개발자 도구에서 요청/응답 확인
3. **API 문서**: `/docs` 엔드포인트에서 Swagger UI 활용
4. **테스트 환경**: 단계별로 테스트하여 문제 격리

## 📊 성능 벤치마크

### 예상 생성 시간
- **Core**: 5-15초
- **SD3.5**: 10-30초  
- **Ultra**: 15-45초
- **제어 API**: 10-25초

### 크레딧 사용량
- **Core**: 3 크레딧
- **SD3.5**: 3.5-6.5 크레딧
- **Ultra**: 8 크레딧
- **제어 API**: 3-8 크레딧

이 테스트 가이드를 따라하면 React + FastAPI 환경에서 Stability AI API를 안정적으로 통합하고 테스트할 수 있습니다.