"""
Stability AI API Client
모든 Stability AI API 호출을 위한 통합 클라이언트
"""

import requests
import os
from typing import Dict, Any, Optional, Union
import streamlit as st


class StabilityAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stability.ai"
        self.headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*"
        }
    
    def _make_request(self, method: str, endpoint: str, files: Optional[Dict] = None, 
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """통합 API 요청 메서드"""
        url = f"{self.base_url}{endpoint}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # 디버그 정보 출력 (개발 환경에서만)
        import os
        if os.getenv("DEBUG", "False").lower() == "true":
            print(f"🔍 API Request Debug:")
            print(f"  URL: {url}")
            print(f"  Method: {method}")
            print(f"  Data: {data}")
            print(f"  Files: {list(files.keys()) if files else None}")
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=request_headers, files=files, data=data)
            elif method.upper() == "GET":
                response = requests.get(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.RequestException as e:
            st.error(f"API 요청 중 오류 발생: {str(e)}")
            raise e

    # 이미지 생성 API들
    def generate_core_image(self, prompt: str, **kwargs) -> requests.Response:
        """Stable Image Core API"""
        endpoint = "/v2beta/stable-image/generate/core"
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"none": ''}
        return self._make_request("POST", endpoint, files=files, data=data)

    def generate_sd35_image(self, prompt: str, image_file=None, **kwargs) -> requests.Response:
        """Stable Diffusion 3.5 API - supports both text-to-image and image-to-image"""
        endpoint = "/v2beta/stable-image/generate/sd3"
        data = {"prompt": prompt}
        data.update(kwargs)
        
        files = {}
        if image_file and kwargs.get("mode") == "image-to-image":
            files["image"] = image_file
        else:
            files["none"] = ''
        
        return self._make_request("POST", endpoint, files=files, data=data)

    def generate_ultra_image(self, prompt: str, image_file=None, **kwargs) -> requests.Response:
        """Stable Image Ultra API"""
        endpoint = "/v2beta/stable-image/generate/ultra"
        data = {"prompt": prompt}
        data.update(kwargs)
        
        files = {}
        if image_file:
            files["image"] = image_file
        else:
            files["none"] = ''
        
        return self._make_request("POST", endpoint, files=files, data=data)

    # 이미지 제어/편집 API들
    def sketch_to_image(self, prompt: str, image_file, **kwargs) -> requests.Response:
        """Sketch ControlNet API"""
        endpoint = "/v2beta/stable-image/control/sketch"
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"image": image_file}
        return self._make_request("POST", endpoint, files=files, data=data)

    def structure_control(self, prompt: str, image_file, **kwargs) -> requests.Response:
        """Structure ControlNet API"""
        endpoint = "/v2beta/stable-image/control/structure"
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"image": image_file}
        return self._make_request("POST", endpoint, files=files, data=data)

    def style_guide(self, prompt: str, image_file, **kwargs) -> requests.Response:
        """Style Guide ControlNet API"""
        endpoint = "/v2beta/stable-image/control/style"
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"image": image_file}
        return self._make_request("POST", endpoint, files=files, data=data)

    def style_transfer(self, init_image, style_image, **kwargs) -> requests.Response:
        """Style Transfer API"""
        endpoint = "/v2beta/stable-image/control/style-transfer"
        data = kwargs
        files = {
            "init_image": init_image,
            "style_image": style_image
        }
        return self._make_request("POST", endpoint, files=files, data=data)

    # 오디오 생성 API들
    def text_to_audio(self, prompt: str, **kwargs) -> requests.Response:
        """Text-to-Audio API"""
        endpoint = "/v2beta/audio/stable-audio-2/text-to-audio"
        headers = {"accept": "audio/*"}
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"none": ''}
        return self._make_request("POST", endpoint, files=files, data=data, headers=headers)

    def audio_to_audio(self, prompt: str, audio_file, **kwargs) -> requests.Response:
        """Audio-to-Audio API"""
        endpoint = "/v2beta/audio/stable-audio-2/audio-to-audio"
        headers = {"accept": "audio/*"}
        data = {"prompt": prompt}
        data.update(kwargs)
        files = {"audio": audio_file}
        return self._make_request("POST", endpoint, files=files, data=data, headers=headers)

    # 3D 생성 API들
    def fast_3d(self, image_file, **kwargs) -> requests.Response:
        """Stable Fast 3D API"""
        endpoint = "/v2beta/3d/stable-fast-3d"
        data = kwargs
        files = {"image": image_file}
        return self._make_request("POST", endpoint, files=files, data=data)

    def point_aware_3d(self, image_file, **kwargs) -> requests.Response:
        """Stable Point Aware 3D API"""
        endpoint = "/v2beta/3d/stable-point-aware-3d"
        data = kwargs
        files = {"image": image_file}
        return self._make_request("POST", endpoint, files=files, data=data)

    # 결과 조회 API
    def get_generation_result(self, generation_id: str) -> requests.Response:
        """비동기 생성 결과 조회"""
        endpoint = f"/v2beta/results/{generation_id}"
        return self._make_request("GET", endpoint)


def get_api_client() -> StabilityAPIClient:
    """API 클라이언트 인스턴스 반환"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        st.error("⚠️ API 키가 설정되지 않았습니다. .env 파일에서 STABILITY_API_KEY를 설정해주세요.")
        st.stop()
    
    return StabilityAPIClient(api_key)