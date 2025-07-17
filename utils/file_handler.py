"""
파일 업로드/다운로드 및 처리 유틸리티
"""

import streamlit as st
import io
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import base64


def validate_image_file(uploaded_file) -> Tuple[bool, str]:
    """이미지 파일 유효성 검사"""
    if uploaded_file is None:
        return False, "파일이 업로드되지 않았습니다."
    
    if uploaded_file.type not in ["image/jpeg", "image/png", "image/webp"]:
        return False, "지원되지 않는 이미지 형식입니다. (JPEG, PNG, WebP만 지원)"
    
    if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
        return False, "파일 크기가 너무 큽니다. (최대 50MB)"
    
    try:
        image = Image.open(uploaded_file)
        width, height = image.size
        
        # 최소 크기 검사
        if width < 64 or height < 64:
            return False, "이미지 크기가 너무 작습니다. (최소 64x64px)"
        
        # 최대 픽셀 수 검사
        if width * height > 9437184:  # 약 3072x3072
            return False, "이미지 픽셀 수가 너무 많습니다. (최대 9,437,184 픽셀)"
        
        # 종횡비 검사
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 2.5:
            return False, "종횡비가 2.5:1을 초과할 수 없습니다."
        
        return True, "유효한 이미지 파일입니다."
    
    except Exception as e:
        return False, f"이미지 파일을 읽을 수 없습니다: {str(e)}"


def validate_audio_file(uploaded_file) -> Tuple[bool, str]:
    """오디오 파일 유효성 검사"""
    if uploaded_file is None:
        return False, "파일이 업로드되지 않았습니다."
    
    if uploaded_file.type not in ["audio/mpeg", "audio/wav", "audio/mp3"]:
        return False, "지원되지 않는 오디오 형식입니다. (MP3, WAV만 지원)"
    
    if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
        return False, "파일 크기가 너무 큽니다. (최대 50MB)"
    
    return True, "유효한 오디오 파일입니다."


def display_image_with_info(image_data: bytes, title: str = "생성된 이미지"):
    """이미지 표시 및 정보 제공"""
    try:
        image = Image.open(io.BytesIO(image_data))
        st.image(image, caption=title, use_container_width=True)
        
        # 이미지 정보 표시
        with st.expander("이미지 정보"):
            st.write(f"**크기**: {image.size[0]} x {image.size[1]} 픽셀")
            st.write(f"**모드**: {image.mode}")
            st.write(f"**파일 크기**: {len(image_data):,} 바이트")
        
        return image
    except Exception as e:
        st.error(f"이미지를 표시할 수 없습니다: {str(e)}")
        return None


def create_download_button(data: bytes, filename: str, mime_type: str, label: str):
    """다운로드 버튼 생성"""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type
    )


def get_image_download_link(image_data: bytes, filename: str) -> str:
    """이미지 다운로드 링크 생성"""
    b64 = base64.b64encode(image_data).decode()
    return f'<a href="data:image/png;base64,{b64}" download="{filename}">다운로드 {filename}</a>'


def process_uploaded_image(uploaded_file) -> Optional[io.BytesIO]:
    """업로드된 이미지 파일 처리"""
    if uploaded_file is None:
        return None
    
    is_valid, message = validate_image_file(uploaded_file)
    if not is_valid:
        st.error(message)
        return None
    
    # 파일 포인터를 처음으로 되돌림
    uploaded_file.seek(0)
    return io.BytesIO(uploaded_file.read())


def process_uploaded_audio(uploaded_file) -> Optional[io.BytesIO]:
    """업로드된 오디오 파일 처리"""
    if uploaded_file is None:
        return None
    
    is_valid, message = validate_audio_file(uploaded_file)
    if not is_valid:
        st.error(message)
        return None
    
    # 파일 포인터를 처음으로 되돌림
    uploaded_file.seek(0)
    return io.BytesIO(uploaded_file.read())


def get_aspect_ratios() -> Dict[str, str]:
    """지원되는 종횡비 목록 반환"""
    return {
        "1:1 (정사각형)": "1:1",
        "16:9 (와이드)": "16:9",
        "9:16 (세로)": "9:16",
        "3:2 (가로)": "3:2",
        "2:3 (세로)": "2:3",
        "4:3 (가로)": "4:3",
        "3:4 (세로)": "3:4"
    }


def get_output_formats() -> Dict[str, str]:
    """지원되는 출력 형식 목록 반환"""
    return {
        "PNG": "png",
        "JPEG": "jpeg", 
        "WebP": "webp"
    }


def get_style_presets() -> Dict[str, str]:
    """스타일 프리셋 목록 반환"""
    return {
        "기본값": "",
        "사진": "photographic",
        "애니메이션": "anime",
        "디지털 아트": "digital-art",
        "3D 모델": "3d-model",
        "픽셀 아트": "pixel-art",
        "영화적": "cinematic",
        "판타지": "fantasy-art",
        "일러스트": "illustration"
    }