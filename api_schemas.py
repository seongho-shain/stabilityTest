"""
Pydantic 스키마 정의
Stability AI API를 위한 요청/응답 모델들
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Union
from enum import Enum


# Enum 정의
class OutputFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class AspectRatio(str, Enum):
    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_3_2 = "3:2"
    PORTRAIT_2_3 = "2:3"
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_3_4 = "3:4"


class StylePreset(str, Enum):
    NONE = ""
    PHOTOGRAPHIC = "photographic"
    ANIME = "anime"
    DIGITAL_ART = "digital-art"
    MODEL_3D = "3d-model"
    PIXEL_ART = "pixel-art"
    CINEMATIC = "cinematic"
    FANTASY_ART = "fantasy-art"
    ILLUSTRATION = "illustration"


class GenerationMode(str, Enum):
    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_TO_IMAGE = "image-to-image"


class SD35Model(str, Enum):
    LARGE = "sd3.5-large"
    LARGE_TURBO = "sd3.5-large-turbo"
    MEDIUM = "sd3.5-medium"


# 기본 스키마
class BaseGenerationRequest(BaseModel):
    """기본 이미지 생성 요청 스키마"""
    prompt: str = Field(..., max_length=10000, description="생성할 이미지에 대한 설명")
    negative_prompt: Optional[str] = Field(None, max_length=10000, description="생성하지 않을 요소들")
    output_format: OutputFormat = Field(OutputFormat.PNG, description="출력 파일 형식")
    style_preset: Optional[StylePreset] = Field(StylePreset.NONE, description="스타일 프리셋")
    seed: Optional[int] = Field(None, ge=0, le=2147483647, description="랜덤 시드 (0 또는 None = 랜덤)")
    
    @validator('prompt')
    def prompt_not_empty(cls, v):
        if not v.strip():
            raise ValueError('프롬프트는 비어있을 수 없습니다')
        return v.strip()


# 이미지 생성 요청 스키마들
class CoreImageRequest(BaseGenerationRequest):
    """Stable Image Core 요청"""
    aspect_ratio: AspectRatio = Field(AspectRatio.SQUARE, description="이미지 종횡비")


class SD35ImageRequest(BaseGenerationRequest):
    """Stable Diffusion 3.5 요청"""
    mode: GenerationMode = Field(GenerationMode.TEXT_TO_IMAGE, description="생성 모드")
    model: SD35Model = Field(SD35Model.LARGE, description="사용할 SD3.5 모델")
    aspect_ratio: Optional[AspectRatio] = Field(AspectRatio.SQUARE, description="이미지 종횡비 (text-to-image 모드에서만)")
    strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="변형 강도 (image-to-image 모드에서 필수)")
    
    @validator('aspect_ratio', always=True)
    def validate_aspect_ratio(cls, v, values):
        if values.get('mode') == GenerationMode.IMAGE_TO_IMAGE:
            return None  # image-to-image 모드에서는 aspect_ratio 사용 안함
        return v or AspectRatio.SQUARE
    
    @validator('strength', always=True)
    def validate_strength(cls, v, values):
        if values.get('mode') == GenerationMode.IMAGE_TO_IMAGE and v is None:
            raise ValueError('image-to-image 모드에서는 strength가 필수입니다')
        return v


class UltraImageRequest(BaseGenerationRequest):
    """Stable Image Ultra 요청"""
    aspect_ratio: AspectRatio = Field(AspectRatio.SQUARE, description="이미지 종횡비")
    strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="참조 이미지 영향도")


# 이미지 제어 요청 스키마들
class BaseControlRequest(BaseGenerationRequest):
    """기본 이미지 제어 요청"""
    control_strength: float = Field(0.7, ge=0.0, le=1.0, description="제어 강도")


class SketchRequest(BaseControlRequest):
    """Sketch ControlNet 요청"""
    pass


class StructureRequest(BaseControlRequest):
    """Structure ControlNet 요청"""
    pass


class StyleGuideRequest(BaseControlRequest):
    """Style Guide ControlNet 요청"""
    fidelity: float = Field(0.5, ge=0.0, le=1.0, description="스타일 충실도")


class StyleTransferRequest(BaseGenerationRequest):
    """Style Transfer 요청"""
    style_strength: float = Field(1.0, ge=0.0, le=1.0, description="스타일 강도")
    composition_fidelity: float = Field(0.9, ge=0.0, le=1.0, description="구성 충실도")
    change_strength: float = Field(0.9, ge=0.1, le=1.0, description="변화 강도")


# 응답 스키마들
class ImageGenerationResponse(BaseModel):
    """이미지 생성 성공 응답"""
    success: bool = True
    message: str = "이미지 생성 완료"
    image_url: Optional[str] = None  # 이미지가 저장된 URL
    filename: str
    file_size: int
    generation_time: float
    credits_used: int


class ErrorResponse(BaseModel):
    """오류 응답"""
    success: bool = False
    error: str
    details: Optional[str] = None
    error_code: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """헬스체크 응답"""
    status: str = "healthy"
    api_available: bool
    timestamp: str


# 파일 업로드 검증을 위한 스키마
class FileValidationResponse(BaseModel):
    """파일 검증 결과"""
    valid: bool
    message: str
    file_info: Optional[dict] = None


# 사용 예제를 위한 샘플 데이터
SAMPLE_REQUESTS = {
    "core": {
        "prompt": "A beautiful sunset over mountains",
        "output_format": "png",
        "aspect_ratio": "16:9",
        "style_preset": "photographic",
        "seed": 12345
    },
    "sd35_text_to_image": {
        "prompt": "A futuristic city at night",
        "mode": "text-to-image",
        "model": "sd3.5-large",
        "aspect_ratio": "16:9",
        "output_format": "png",
        "style_preset": "digital-art"
    },
    "sd35_image_to_image": {
        "prompt": "Transform this into a painting",
        "mode": "image-to-image",
        "model": "sd3.5-large",
        "strength": 0.8,
        "output_format": "png",
        "style_preset": "digital-art"
    },
    "ultra": {
        "prompt": "A professional portrait photo",
        "aspect_ratio": "3:4",
        "output_format": "jpeg",
        "style_preset": "photographic"
    },
    "sketch": {
        "prompt": "A detailed castle on a hill",
        "control_strength": 0.7,
        "output_format": "png",
        "style_preset": "fantasy-art"
    },
    "style_transfer": {
        "prompt": "Enhance the artistic style",
        "style_strength": 1.0,
        "composition_fidelity": 0.9,
        "change_strength": 0.9,
        "output_format": "png"
    }
}


# 유틸리티 함수들
def validate_request_for_model(model_type: str, request_data: dict) -> dict:
    """모델 타입에 따라 요청 데이터를 검증하고 정리"""
    if model_type == "core":
        return CoreImageRequest(**request_data).dict(exclude_none=True)
    elif model_type == "sd35":
        return SD35ImageRequest(**request_data).dict(exclude_none=True)
    elif model_type == "ultra":
        return UltraImageRequest(**request_data).dict(exclude_none=True)
    elif model_type == "sketch":
        return SketchRequest(**request_data).dict(exclude_none=True)
    elif model_type == "structure":
        return StructureRequest(**request_data).dict(exclude_none=True)
    elif model_type == "style_guide":
        return StyleGuideRequest(**request_data).dict(exclude_none=True)
    elif model_type == "style_transfer":
        return StyleTransferRequest(**request_data).dict(exclude_none=True)
    else:
        raise ValueError(f"지원되지 않는 모델 타입: {model_type}")


def get_sample_request(model_type: str) -> dict:
    """모델 타입에 해당하는 샘플 요청 데이터 반환"""
    return SAMPLE_REQUESTS.get(model_type, {})