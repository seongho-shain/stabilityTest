# 🎨 Stability AI 종합 테스트 플랫폼

Stability AI의 모든 주요 API 기능을 하나의 통합된 Streamlit 웹 애플리케이션에서 테스트할 수 있는 플랫폼입니다.

## ✨ 주요 기능

### 🎨 이미지 생성
- **Stable Image Core**: 기본 텍스트→이미지 생성
- **Stable Diffusion 3.5**: 고급 이미지 생성 (Large/Medium/Turbo 모델)
- **Stable Image Ultra**: 최고급 품질의 이미지 생성

### 🎛️ 이미지 제어/편집
- **Sketch ControlNet**: 스케치를 상세한 이미지로 변환
- **Structure ControlNet**: 구조를 보존하며 이미지 생성
- **Style Guide ControlNet**: 스타일 참조 이미지로 생성
- **Style Transfer**: 두 이미지 간 스타일 전송

### 🎵 오디오 생성
- **Text-to-Audio**: 텍스트 설명으로 음악/효과음 생성
- **Audio-to-Audio**: 기존 오디오를 다른 스타일로 변환

### 🎭 3D 모델 생성
- **Stable Fast 3D**: 빠른 2D→3D 변환
- **Stable Point Aware 3D**: 고품질 3D 모델 생성

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
`.env` 파일에서 Stability AI API 키를 설정하세요:
```
STABILITY_API_KEY=your-actual-api-key-here
```

### 3. 애플리케이션 실행
```bash
streamlit run main.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

## 📋 사용 방법

### 기본 사용법
1. 사이드바에서 사용할 기능 카테고리를 선택합니다
2. 하위 기능을 선택합니다
3. 필요한 입력(텍스트, 이미지, 오디오)을 제공합니다
4. 매개변수를 조정합니다
5. 생성 버튼을 클릭합니다

### 이미지 생성
- **프롬프트**: 생성하고 싶은 이미지를 상세히 설명
- **네거티브 프롬프트**: 생성하지 않을 요소들 지정
- **종횡비**: 출력 이미지의 비율 선택
- **스타일 프리셋**: 사진, 애니메이션, 디지털 아트 등

### 이미지 제어/편집
- **Sketch**: 스케치나 선화를 업로드하여 상세한 이미지로 변환
- **Structure**: 구조를 유지하면서 새로운 이미지 생성
- **Style Guide**: 참조 이미지의 스타일을 적용
- **Style Transfer**: 두 이미지의 스타일을 조합

### 오디오 생성
- **Text-to-Audio**: "잔잔한 피아노 멜로디", "비 오는 소리" 등 설명
- **Audio-to-Audio**: 기존 오디오 파일을 다른 스타일로 변환
- **길이**: 1-190초까지 설정 가능
- **품질**: 샘플링 스텝 조정으로 품질 제어

### 3D 모델 생성
- **입력**: 명확한 객체가 있는 2D 이미지
- **텍스처 해상도**: 512, 1024, 2048px 선택
- **메시 최적화**: Blender/Unity 사용 시 quad 권장
- **출력**: GLB 형식 (glTF Binary)

## ⚙️ 고급 설정

### 매개변수 설명
- **CFG Scale**: 프롬프트 준수도 (1-25, 높을수록 정확)
- **시드**: 동일한 결과 재생성용 (0 = 랜덤)
- **강도**: 입력 이미지의 영향도 (0-1)
- **제어 강도**: ControlNet의 영향력 조절

### 파일 제한사항
- **이미지**: 최대 50MB, 최소 64x64px, 최대 약 3K x 3K
- **오디오**: MP3/WAV, 최대 50MB, 6-190초
- **종횡비**: 1:2.5 ~ 2.5:1 범위

## 💡 사용 팁

### 좋은 프롬프트 작성법
- 구체적이고 상세한 설명 사용
- 스타일, 조명, 분위기 등 세부 사항 포함
- 네거티브 프롬프트로 원하지 않는 요소 제거

### 이미지 업로드 팁
- **스케치**: 명확한 선화, 단순한 배경
- **3D 변환**: 배경이 단순하고 객체가 명확한 이미지
- **스타일 참조**: 원하는 스타일이 잘 드러나는 이미지

### 오디오 생성 팁
- 장르, 악기, 분위기를 구체적으로 명시
- 템포나 리듬 패턴도 설명에 포함
- 참조할 만한 음악 스타일 언급

## 📁 프로젝트 구조
```
stability-test/
├── main.py                 # 메인 Streamlit 애플리케이션
├── requirements.txt        # Python 의존성
├── .env                    # API 키 설정
├── utils/
│   ├── api_client.py      # Stability AI API 클라이언트
│   ├── file_handler.py    # 파일 처리 유틸리티
│   └── ui_components.py   # UI 컴포넌트
└── *.md                   # API 문서들
```

## 🔧 문제 해결

### API 키 오류
- `.env` 파일에서 `STABILITY_API_KEY` 확인
- API 키가 유효한지 Stability AI 대시보드에서 확인

### 파일 업로드 오류
- 파일 크기와 형식 제한 확인
- 이미지 해상도와 종횡비 제한 확인

### 생성 실패
- 프롬프트가 Stability AI 정책에 위반되지 않는지 확인
- 네트워크 연결 상태 확인
- API 크레딧 잔액 확인

## 📚 추가 리소스
- [Stability AI API 문서](https://platform.stability.ai/docs)
- [Streamlit 문서](https://docs.streamlit.io)

## 📄 라이선스
이 프로젝트는 테스트 목적으로 제작되었습니다. Stability AI의 이용 약관을 준수하여 사용하세요.