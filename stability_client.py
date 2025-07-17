"""
순수 Python Stability AI API 클라이언트
FastAPI/React 환경에서 사용하기 위한 깨끗한 API 클라이언트
"""

import requests
import os
import io
from typing import Dict, Any, Optional, Union, BinaryIO
from PIL import Image
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StabilityClientError(Exception):
    """Stability AI API 관련 에러"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class StabilityClient:
    """
    Stability AI API 클라이언트
    
    Usage:
        client = StabilityClient(api_key="your-api-key")
        result = client.generate_core_image("A beautiful sunset", output_format="png")
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.stability.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*",
            "User-Agent": "StabilityClient/1.0"
        })
    
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     data: Optional[Dict[str, Any]] = None,
                     files: Optional[Dict[str, Any]] = None,
                     timeout: int = 60) -> requests.Response:
        """
        통합 API 요청 메서드
        
        Args:
            method: HTTP 메서드 (GET, POST)
            endpoint: API 엔드포인트
            data: 폼 데이터
            files: 파일 데이터
            timeout: 타임아웃 (초)
        
        Returns:
            requests.Response 객체
        
        Raises:
            StabilityClientError: API 요청 실패 시
        """
        url = f"{self.base_url}{endpoint}"
        
        # 디버그 로그
        logger.debug(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Data: {data}")
        if files:
            logger.debug(f"Files: {list(files.keys())}")
        
        try:
            if method.upper() == "POST":
                response = self.session.post(url, data=data, files=files, timeout=timeout)
            elif method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=timeout)
            else:
                raise ValueError(f"지원되지 않는 HTTP 메서드: {method}")
            
            # 응답 검증
            if response.status_code == 200:
                return response
            elif response.status_code == 202:
                # 비동기 작업 진행 중
                return response
            else:
                # 에러 응답 처리
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "알 수 없는 오류")
                except:
                    error_message = response.text or f"HTTP {response.status_code} 오류"
                
                raise StabilityClientError(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=error_data if 'error_data' in locals() else None
                )
        
        except requests.RequestException as e:
            raise StabilityClientError(f"네트워크 오류: {str(e)}")
    
    def _prepare_image_file(self, image: Union[str, bytes, BinaryIO, Image.Image]) -> BinaryIO:
        """
        이미지 파일을 API 요청에 적합한 형태로 변환
        
        Args:
            image: 이미지 (파일 경로, bytes, file object, PIL Image)
        
        Returns:
            BinaryIO 객체
        """
        if isinstance(image, str):
            # 파일 경로
            return open(image, "rb")
        elif isinstance(image, bytes):
            # bytes 데이터
            return io.BytesIO(image)
        elif isinstance(image, Image.Image):
            # PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer
        elif hasattr(image, 'read'):
            # file-like object
            return image
        else:
            raise ValueError("지원되지 않는 이미지 형식")
    
    def validate_image_file(self, image_file: BinaryIO) -> Dict[str, Any]:
        """
        이미지 파일 유효성 검사
        
        Args:
            image_file: 이미지 파일 객체
        
        Returns:
            검증 결과 딕셔너리
        """
        try:
            # 파일 크기 확인
            image_file.seek(0, 2)  # 파일 끝으로 이동
            file_size = image_file.tell()
            image_file.seek(0)  # 파일 시작으로 복귀
            
            if file_size > 50 * 1024 * 1024:  # 50MB
                return {"valid": False, "error": "파일 크기가 50MB를 초과합니다"}
            
            # 이미지 형식 및 크기 확인
            image = Image.open(image_file)
            width, height = image.size
            
            if width < 64 or height < 64:
                return {"valid": False, "error": "이미지 크기가 너무 작습니다 (최소 64x64px)"}
            
            if width * height > 9437184:  # 약 3072x3072
                return {"valid": False, "error": "이미지 픽셀 수가 너무 많습니다"}
            
            # 종횡비 확인
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 2.5:
                return {"valid": False, "error": "종횡비가 2.5:1을 초과합니다"}
            
            image_file.seek(0)  # 파일 시작으로 복귀
            
            return {
                "valid": True,
                "info": {
                    "width": width,
                    "height": height,
                    "format": image.format,
                    "mode": image.mode,
                    "size_bytes": file_size
                }
            }
        
        except Exception as e:
            return {"valid": False, "error": f"이미지 파일을 읽을 수 없습니다: {str(e)}"}
    
    # 이미지 생성 API들
    
    def generate_core_image(self, 
                           prompt: str,
                           aspect_ratio: str = "1:1",
                           output_format: str = "png",
                           style_preset: Optional[str] = None,
                           negative_prompt: Optional[str] = None,
                           seed: Optional[int] = None) -> bytes:
        """
        Stable Image Core로 이미지 생성
        
        Args:
            prompt: 이미지 설명
            aspect_ratio: 이미지 비율 (1:1, 16:9, 9:16, 3:2, 2:3, 4:3, 3:4)
            output_format: 출력 형식 (png, jpeg, webp)
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/generate/core"
        
        data = {"prompt": prompt}
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if output_format:
            data["output_format"] = output_format
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        files = {"none": ""}
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    def generate_sd35_image(self,
                           prompt: str,
                           mode: str = "text-to-image",
                           model: str = "sd3.5-large",
                           image: Optional[Union[str, bytes, BinaryIO]] = None,
                           strength: Optional[float] = None,
                           aspect_ratio: Optional[str] = "1:1",
                           output_format: str = "png",
                           style_preset: Optional[str] = None,
                           negative_prompt: Optional[str] = None,
                           seed: Optional[int] = None) -> bytes:
        """
        Stable Diffusion 3.5로 이미지 생성
        
        Args:
            prompt: 이미지 설명
            mode: 생성 모드 (text-to-image, image-to-image)
            model: 모델 버전 (sd3.5-large, sd3.5-large-turbo, sd3.5-medium)
            image: 입력 이미지 (image-to-image 모드에서 필수)
            strength: 변형 강도 (image-to-image 모드에서 필수, 0.0-1.0)
            aspect_ratio: 이미지 비율 (text-to-image 모드에서만)
            output_format: 출력 형식
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/generate/sd3"
        
        data = {
            "prompt": prompt,
            "mode": mode,
            "model": model
        }
        
        # 모드별 파라미터 처리
        if mode == "image-to-image":
            if image is None:
                raise ValueError("image-to-image 모드에서는 입력 이미지가 필요합니다")
            if strength is None:
                raise ValueError("image-to-image 모드에서는 strength가 필요합니다")
            data["strength"] = strength
        else:  # text-to-image
            if aspect_ratio:
                data["aspect_ratio"] = aspect_ratio
        
        if output_format:
            data["output_format"] = output_format
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        files = {}
        if mode == "image-to-image" and image:
            image_file = self._prepare_image_file(image)
            files["image"] = image_file
        else:
            files["none"] = ""
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    def generate_ultra_image(self,
                            prompt: str,
                            image: Optional[Union[str, bytes, BinaryIO]] = None,
                            strength: Optional[float] = None,
                            aspect_ratio: str = "1:1",
                            output_format: str = "png",
                            style_preset: Optional[str] = None,
                            negative_prompt: Optional[str] = None,
                            seed: Optional[int] = None) -> bytes:
        """
        Stable Image Ultra로 이미지 생성
        
        Args:
            prompt: 이미지 설명
            image: 참조 이미지 (선택사항)
            strength: 참조 이미지 영향도 (0.0-1.0)
            aspect_ratio: 이미지 비율
            output_format: 출력 형식
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/generate/ultra"
        
        data = {"prompt": prompt}
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if output_format:
            data["output_format"] = output_format
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        if strength is not None:
            data["strength"] = strength
        
        files = {}
        if image:
            image_file = self._prepare_image_file(image)
            files["image"] = image_file
        else:
            files["none"] = ""
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    # 이미지 제어/편집 API들
    
    def sketch_to_image(self,
                       prompt: str,
                       image: Union[str, bytes, BinaryIO],
                       control_strength: float = 0.7,
                       output_format: str = "png",
                       style_preset: Optional[str] = None,
                       negative_prompt: Optional[str] = None,
                       seed: Optional[int] = None) -> bytes:
        """
        스케치를 이미지로 변환
        
        Args:
            prompt: 이미지 설명
            image: 스케치 이미지
            control_strength: 제어 강도 (0.0-1.0)
            output_format: 출력 형식
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/control/sketch"
        
        data = {
            "prompt": prompt,
            "control_strength": control_strength
        }
        if output_format:
            data["output_format"] = output_format
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        image_file = self._prepare_image_file(image)
        files = {"image": image_file}
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    def structure_control(self,
                         prompt: str,
                         image: Union[str, bytes, BinaryIO],
                         control_strength: float = 0.7,
                         output_format: str = "png",
                         style_preset: Optional[str] = None,
                         negative_prompt: Optional[str] = None,
                         seed: Optional[int] = None) -> bytes:
        """
        구조 제어로 이미지 생성
        
        Args:
            prompt: 이미지 설명
            image: 구조 참조 이미지
            control_strength: 제어 강도 (0.0-1.0)
            output_format: 출력 형식
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/control/structure"
        
        data = {
            "prompt": prompt,
            "control_strength": control_strength
        }
        if output_format:
            data["output_format"] = output_format
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        image_file = self._prepare_image_file(image)
        files = {"image": image_file}
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    def style_guide(self,
                   prompt: str,
                   image: Union[str, bytes, BinaryIO],
                   fidelity: float = 0.5,
                   output_format: str = "png",
                   aspect_ratio: str = "1:1",
                   style_preset: Optional[str] = None,
                   negative_prompt: Optional[str] = None,
                   seed: Optional[int] = None) -> bytes:
        """
        스타일 가이드로 이미지 생성
        
        Args:
            prompt: 이미지 설명
            image: 스타일 참조 이미지
            fidelity: 스타일 충실도 (0.0-1.0)
            output_format: 출력 형식
            aspect_ratio: 이미지 비율
            style_preset: 스타일 프리셋
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/control/style"
        
        data = {
            "prompt": prompt,
            "fidelity": fidelity
        }
        if output_format:
            data["output_format"] = output_format
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if style_preset:
            data["style_preset"] = style_preset
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        image_file = self._prepare_image_file(image)
        files = {"image": image_file}
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    def style_transfer(self,
                      init_image: Union[str, bytes, BinaryIO],
                      style_image: Union[str, bytes, BinaryIO],
                      prompt: Optional[str] = None,
                      style_strength: float = 1.0,
                      composition_fidelity: float = 0.9,
                      change_strength: float = 0.9,
                      output_format: str = "png",
                      negative_prompt: Optional[str] = None,
                      seed: Optional[int] = None) -> bytes:
        """
        스타일 전송
        
        Args:
            init_image: 원본 이미지
            style_image: 스타일 이미지
            prompt: 이미지 설명 (선택사항)
            style_strength: 스타일 강도 (0.0-1.0)
            composition_fidelity: 구성 충실도 (0.0-1.0)
            change_strength: 변화 강도 (0.1-1.0)
            output_format: 출력 형식
            negative_prompt: 네거티브 프롬프트
            seed: 랜덤 시드
        
        Returns:
            생성된 이미지 bytes
        """
        endpoint = "/v2beta/stable-image/control/style-transfer"
        
        data = {
            "style_strength": style_strength,
            "composition_fidelity": composition_fidelity,
            "change_strength": change_strength
        }
        if prompt:
            data["prompt"] = prompt
        if output_format:
            data["output_format"] = output_format
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed
        
        init_file = self._prepare_image_file(init_image)
        style_file = self._prepare_image_file(style_image)
        
        files = {
            "init_image": init_file,
            "style_image": style_file
        }
        
        response = self._make_request("POST", endpoint, data=data, files=files)
        return response.content
    
    # 유틸리티 메서드들
    
    def save_image(self, image_bytes: bytes, filename: str) -> str:
        """
        이미지 bytes를 파일로 저장
        
        Args:
            image_bytes: 이미지 데이터
            filename: 저장할 파일명
        
        Returns:
            저장된 파일 경로
        """
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return filename
    
    def get_image_info(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        이미지 정보 반환
        
        Args:
            image_bytes: 이미지 데이터
        
        Returns:
            이미지 정보 딕셔너리
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_bytes)
            }
        except Exception as e:
            return {"error": str(e)}


# 사용 예제
if __name__ == "__main__":
    # 예제 사용법
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        print("STABILITY_API_KEY 환경변수를 설정해주세요")
        exit(1)
    
    client = StabilityClient(api_key)
    
    try:
        # Core 이미지 생성 예제
        print("Core 이미지 생성 중...")
        image_data = client.generate_core_image(
            prompt="A beautiful sunset over mountains",
            aspect_ratio="16:9",
            style_preset="photographic"
        )
        
        # 이미지 저장
        filename = client.save_image(image_data, "sunset.png")
        print(f"이미지 저장 완료: {filename}")
        
        # 이미지 정보 출력
        info = client.get_image_info(image_data)
        print(f"이미지 정보: {info}")
        
    except StabilityClientError as e:
        print(f"API 오류: {e}")
        if e.status_code:
            print(f"상태 코드: {e.status_code}")
    except Exception as e:
        print(f"일반 오류: {e}")