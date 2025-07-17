"""
FastAPI 백엔드 예제
Stability AI API를 React 프론트엔드에서 사용하기 위한 백엔드 서버
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, ValidationError
import uvicorn
import os
import io
import time
import uuid
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# 로컬 모듈 임포트
from api_schemas import *
from stability_client import StabilityClient, StabilityClientError

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Stability AI Image Generation API",
    description="React + FastAPI를 위한 Stability AI 이미지 생성 백엔드",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (React 앱에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
stability_client: Optional[StabilityClient] = None
generation_tasks: Dict[str, Dict] = {}  # 비동기 작업 추적


# 의존성 함수들
async def get_stability_client() -> StabilityClient:
    """Stability AI 클라이언트 의존성"""
    global stability_client
    if stability_client is None:
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="STABILITY_API_KEY 환경변수가 설정되지 않았습니다"
            )
        stability_client = StabilityClient(api_key)
    return stability_client


def validate_file_upload(file: UploadFile) -> None:
    """파일 업로드 검증"""
    # MIME 타입 검증
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"지원되지 않는 파일 형식입니다. 허용된 형식: {', '.join(allowed_types)}"
        )
    
    # 파일 크기 검증 (50MB)
    if hasattr(file, 'size') and file.size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="파일 크기가 50MB를 초과합니다"
        )


# 헬스체크 엔드포인트
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """서버 상태 확인"""
    try:
        client = await get_stability_client()
        api_available = True
    except:
        api_available = False
    
    return HealthCheckResponse(
        api_available=api_available,
        timestamp=datetime.now().isoformat()
    )


# 이미지 생성 엔드포인트들

@app.post("/api/image/generate/core", response_model=ImageGenerationResponse)
async def generate_core_image(
    request: CoreImageRequest,
    client: StabilityClient = Depends(get_stability_client)
):
    """Stable Image Core로 이미지 생성"""
    try:
        start_time = time.time()
        
        # API 호출
        image_data = client.generate_core_image(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            output_format=request.output_format,
            style_preset=request.style_preset,
            negative_prompt=request.negative_prompt,
            seed=request.seed
        )
        
        generation_time = time.time() - start_time
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"core_image_{timestamp}.{request.output_format}"
        
        # 이미지 정보
        image_info = client.get_image_info(image_data)
        
        return ImageGenerationResponse(
            filename=filename,
            file_size=len(image_data),
            generation_time=generation_time,
            credits_used=3
        )
    
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Core 이미지 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다")


@app.post("/api/image/generate/sd35")
async def generate_sd35_image(
    # 폼 데이터로 받기
    prompt: str = Form(...),
    mode: str = Form("text-to-image"),
    model: str = Form("sd3.5-large"),
    aspect_ratio: Optional[str] = Form("1:1"),
    strength: Optional[float] = Form(None),
    output_format: str = Form("png"),
    style_preset: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    client: StabilityClient = Depends(get_stability_client)
):
    """Stable Diffusion 3.5로 이미지 생성"""
    try:
        # 요청 데이터 검증
        request_data = {
            "prompt": prompt,
            "mode": mode,
            "model": model,
            "output_format": output_format
        }
        
        if aspect_ratio and mode == "text-to-image":
            request_data["aspect_ratio"] = aspect_ratio
        if strength is not None:
            request_data["strength"] = strength
        if style_preset:
            request_data["style_preset"] = style_preset
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        # Pydantic 검증
        validated_request = SD35ImageRequest(**request_data)
        
        # 파일 검증
        image_file = None
        if image and mode == "image-to-image":
            validate_file_upload(image)
            image_file = await image.read()
        
        start_time = time.time()
        
        # API 호출
        image_data = client.generate_sd35_image(
            prompt=validated_request.prompt,
            mode=validated_request.mode,
            model=validated_request.model,
            image=image_file,
            strength=validated_request.strength,
            aspect_ratio=validated_request.aspect_ratio,
            output_format=validated_request.output_format,
            style_preset=validated_request.style_preset,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        generation_time = time.time() - start_time
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode_suffix = "i2i" if mode == "image-to-image" else "t2i"
        filename = f"sd35_{mode_suffix}_{timestamp}.{validated_request.output_format}"
        
        # 이미지를 base64로 인코딩하여 반환 (또는 StreamingResponse 사용)
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"SD3.5 이미지 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다")


@app.post("/api/image/generate/ultra")
async def generate_ultra_image(
    prompt: str = Form(...),
    aspect_ratio: str = Form("1:1"),
    strength: Optional[float] = Form(None),
    output_format: str = Form("png"),
    style_preset: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    client: StabilityClient = Depends(get_stability_client)
):
    """Stable Image Ultra로 이미지 생성"""
    try:
        # 요청 데이터 검증
        request_data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format
        }
        if strength is not None:
            request_data["strength"] = strength
        if style_preset:
            request_data["style_preset"] = style_preset
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        validated_request = UltraImageRequest(**request_data)
        
        # 파일 처리
        image_file = None
        if image:
            validate_file_upload(image)
            image_file = await image.read()
        
        start_time = time.time()
        
        # API 호출
        image_data = client.generate_ultra_image(
            prompt=validated_request.prompt,
            image=image_file,
            strength=validated_request.strength,
            aspect_ratio=validated_request.aspect_ratio,
            output_format=validated_request.output_format,
            style_preset=validated_request.style_preset,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        generation_time = time.time() - start_time
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ultra_image_{timestamp}.{validated_request.output_format}"
        
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Ultra 이미지 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다")


# 이미지 제어/편집 엔드포인트들

@app.post("/api/image/control/sketch")
async def sketch_to_image(
    prompt: str = Form(...),
    control_strength: float = Form(0.7),
    output_format: str = Form("png"),
    style_preset: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    image: UploadFile = File(...),
    client: StabilityClient = Depends(get_stability_client)
):
    """스케치를 이미지로 변환"""
    try:
        validate_file_upload(image)
        image_data = await image.read()
        
        # 요청 데이터 검증
        request_data = {
            "prompt": prompt,
            "control_strength": control_strength,
            "output_format": output_format
        }
        if style_preset:
            request_data["style_preset"] = style_preset
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        validated_request = SketchRequest(**request_data)
        
        start_time = time.time()
        
        # API 호출
        result_data = client.sketch_to_image(
            prompt=validated_request.prompt,
            image=image_data,
            control_strength=validated_request.control_strength,
            output_format=validated_request.output_format,
            style_preset=validated_request.style_preset,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sketch_result_{timestamp}.{validated_request.output_format}"
        
        return StreamingResponse(
            io.BytesIO(result_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Sketch 변환 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 변환 중 오류가 발생했습니다")


@app.post("/api/image/control/structure")
async def structure_control(
    prompt: str = Form(...),
    control_strength: float = Form(0.7),
    output_format: str = Form("png"),
    style_preset: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    image: UploadFile = File(...),
    client: StabilityClient = Depends(get_stability_client)
):
    """구조 제어로 이미지 생성"""
    try:
        validate_file_upload(image)
        image_data = await image.read()
        
        request_data = {
            "prompt": prompt,
            "control_strength": control_strength,
            "output_format": output_format
        }
        if style_preset:
            request_data["style_preset"] = style_preset
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        validated_request = StructureRequest(**request_data)
        
        result_data = client.structure_control(
            prompt=validated_request.prompt,
            image=image_data,
            control_strength=validated_request.control_strength,
            output_format=validated_request.output_format,
            style_preset=validated_request.style_preset,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"structure_result_{timestamp}.{validated_request.output_format}"
        
        return StreamingResponse(
            io.BytesIO(result_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Structure 제어 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다")


@app.post("/api/image/control/style-guide")
async def style_guide_control(
    prompt: str = Form(...),
    fidelity: float = Form(0.5),
    aspect_ratio: str = Form("1:1"),
    output_format: str = Form("png"),
    style_preset: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    image: UploadFile = File(...),
    client: StabilityClient = Depends(get_stability_client)
):
    """스타일 가이드로 이미지 생성"""
    try:
        validate_file_upload(image)
        image_data = await image.read()
        
        request_data = {
            "prompt": prompt,
            "fidelity": fidelity,
            "output_format": output_format
        }
        if style_preset:
            request_data["style_preset"] = style_preset
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        validated_request = StyleGuideRequest(**request_data)
        
        result_data = client.style_guide(
            prompt=validated_request.prompt,
            image=image_data,
            fidelity=validated_request.fidelity,
            output_format=validated_request.output_format,
            aspect_ratio=aspect_ratio,
            style_preset=validated_request.style_preset,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"style_guide_result_{timestamp}.{validated_request.output_format}"
        
        return StreamingResponse(
            io.BytesIO(result_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Style Guide 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다")


@app.post("/api/image/control/style-transfer")
async def style_transfer(
    style_strength: float = Form(1.0),
    composition_fidelity: float = Form(0.9),
    change_strength: float = Form(0.9),
    output_format: str = Form("png"),
    prompt: Optional[str] = Form(None),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    init_image: UploadFile = File(...),
    style_image: UploadFile = File(...),
    client: StabilityClient = Depends(get_stability_client)
):
    """스타일 전송"""
    try:
        validate_file_upload(init_image)
        validate_file_upload(style_image)
        
        init_data = await init_image.read()
        style_data = await style_image.read()
        
        request_data = {
            "style_strength": style_strength,
            "composition_fidelity": composition_fidelity,
            "change_strength": change_strength,
            "output_format": output_format
        }
        if prompt:
            request_data["prompt"] = prompt
        if negative_prompt:
            request_data["negative_prompt"] = negative_prompt
        if seed is not None:
            request_data["seed"] = seed
        
        validated_request = StyleTransferRequest(**request_data)
        
        result_data = client.style_transfer(
            init_image=init_data,
            style_image=style_data,
            prompt=validated_request.prompt,
            style_strength=validated_request.style_strength,
            composition_fidelity=validated_request.composition_fidelity,
            change_strength=validated_request.change_strength,
            output_format=validated_request.output_format,
            negative_prompt=validated_request.negative_prompt,
            seed=validated_request.seed
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"style_transfer_{timestamp}.{validated_request.output_format}"
        
        return StreamingResponse(
            io.BytesIO(result_data),
            media_type=f"image/{validated_request.output_format}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"입력 데이터 오류: {str(e)}")
    except StabilityClientError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Style Transfer 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="스타일 전송 중 오류가 발생했습니다")


# 유틸리티 엔드포인트들

@app.post("/api/validate-image")
async def validate_image(image: UploadFile = File(...)):
    """이미지 파일 검증"""
    try:
        validate_file_upload(image)
        image_data = await image.read()
        
        # StabilityClient를 통한 상세 검증
        client = await get_stability_client()
        validation_result = client.validate_image_file(io.BytesIO(image_data))
        
        return FileValidationResponse(
            valid=validation_result["valid"],
            message=validation_result.get("error", "유효한 이미지 파일입니다"),
            file_info=validation_result.get("info")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return FileValidationResponse(
            valid=False,
            message=f"검증 중 오류 발생: {str(e)}"
        )


@app.get("/api/constants")
async def get_constants():
    """프론트엔드에서 사용할 상수들 반환"""
    return {
        "output_formats": [e.value for e in OutputFormat],
        "aspect_ratios": [e.value for e in AspectRatio],
        "style_presets": [e.value for e in StylePreset],
        "sd35_models": [e.value for e in SD35Model],
        "generation_modes": [e.value for e in GenerationMode]
    }


# 예외 처리기
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "입력 데이터 오류", "details": str(exc)}
    )


@app.exception_handler(StabilityClientError)
async def stability_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={"error": str(exc), "details": exc.response_data}
    )


# 서버 실행
if __name__ == "__main__":
    uvicorn.run(
        "fastapi_backend_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )