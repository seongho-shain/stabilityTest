"""
재사용 가능한 UI 컴포넌트들
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
from utils.file_handler import get_aspect_ratios, get_output_formats, get_style_presets


def create_prompt_input(label: str = "프롬프트", help_text: str = None, max_chars: int = 10000) -> str:
    """프롬프트 입력 필드 생성"""
    return st.text_area(
        label,
        help=help_text or f"최대 {max_chars:,}자까지 입력 가능합니다.",
        max_chars=max_chars,
        height=100
    )


def create_generation_mode_selector(model_name: str) -> str:
    """생성 모드 선택기 생성"""
    if model_name == "sd3.5":
        return st.radio(
            "생성 모드",
            ["Text-to-Image", "Image-to-Image"],
            help="Text-to-Image: 텍스트만으로 생성 | Image-to-Image: 입력 이미지를 프롬프트로 변형"
        )
    elif model_name == "ultra":
        return st.radio(
            "생성 모드", 
            ["Text-to-Image", "Text+Image-to-Image"],
            help="Text-to-Image: 텍스트만으로 생성 | Text+Image-to-Image: 참조 이미지와 텍스트 조합"
        )
    else:
        return "Text-to-Image"  # Core 모델은 텍스트만 지원


def create_negative_prompt_input() -> str:
    """네거티브 프롬프트 입력 필드 생성"""
    return st.text_area(
        "네거티브 프롬프트 (선택사항)",
        help="생성하지 않을 요소들을 입력하세요.",
        height=60
    )


def create_basic_image_controls(show_aspect_ratio: bool = True) -> Dict[str, Any]:
    """기본 이미지 생성 제어 옵션들"""
    col1, col2 = st.columns(2)
    
    with col1:
        if show_aspect_ratio:
            aspect_ratios = get_aspect_ratios()
            aspect_ratio = st.selectbox(
                "종횡비",
                options=list(aspect_ratios.keys()),
                index=0
            )
        
        output_formats = get_output_formats()
        output_format = st.selectbox(
            "출력 형식",
            options=list(output_formats.keys()),
            index=0
        )
    
    with col2:
        style_presets = get_style_presets()
        style_preset = st.selectbox(
            "스타일 프리셋",
            options=list(style_presets.keys()),
            index=0
        )
        
        seed = st.number_input(
            "시드 (0 = 랜덤)",
            min_value=0,
            max_value=2147483647,
            value=0,
            help="같은 시드 값으로 동일한 결과를 재생성할 수 있습니다."
        )
    
    controls = {
        "output_format": output_formats[output_format],
        "style_preset": style_presets[style_preset] if style_presets[style_preset] else None,
        "seed": seed if seed > 0 else None
    }
    
    if show_aspect_ratio:
        controls["aspect_ratio"] = aspect_ratios[aspect_ratio]
    
    return controls


def create_advanced_controls(show_cfg_scale: bool = True, show_steps: bool = False, 
                           show_strength: bool = False, show_control_strength: bool = False) -> Dict[str, Any]:
    """고급 제어 옵션들"""
    controls = {}
    
    with st.expander("고급 설정"):
        col1, col2 = st.columns(2)
        
        with col1:
            if show_cfg_scale:
                controls["cfg_scale"] = st.slider(
                    "CFG Scale (프롬프트 준수도)",
                    min_value=1.0,
                    max_value=25.0,
                    value=7.0,
                    step=0.5,
                    help="높을수록 프롬프트를 더 정확히 따릅니다."
                )
            
            if show_steps:
                controls["steps"] = st.slider(
                    "샘플링 스텝",
                    min_value=30,
                    max_value=100,
                    value=50,
                    help="더 많은 스텝은 품질을 향상시키지만 시간이 더 걸립니다."
                )
        
        with col2:
            if show_strength:
                controls["strength"] = st.slider(
                    "변형 강도",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.8,
                    step=0.1,
                    help="입력 이미지를 얼마나 많이 변형할지 결정합니다."
                )
            
            if show_control_strength:
                controls["control_strength"] = st.slider(
                    "제어 강도",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="입력 이미지의 구조나 스타일 영향도를 조절합니다."
                )
    
    # None 값 제거
    return {k: v for k, v in controls.items() if v is not None}


def create_audio_controls() -> Dict[str, Any]:
    """오디오 생성 제어 옵션들"""
    col1, col2 = st.columns(2)
    
    with col1:
        output_format = st.selectbox(
            "출력 형식",
            options=["MP3", "WAV"],
            index=0
        )
        
        duration = st.slider(
            "길이 (초)",
            min_value=1,
            max_value=190,
            value=20,
            help="생성할 오디오의 길이를 설정합니다."
        )
    
    with col2:
        steps = st.slider(
            "샘플링 스텝",
            min_value=30,
            max_value=100,
            value=50,
            help="더 많은 스텝은 품질을 향상시킵니다."
        )
        
        cfg_scale = st.slider(
            "CFG Scale",
            min_value=1.0,
            max_value=25.0,
            value=7.0,
            step=0.5
        )
    
    return {
        "output_format": output_format.lower(),
        "duration": duration,
        "steps": steps,
        "cfg_scale": cfg_scale
    }


def create_3d_controls() -> Dict[str, Any]:
    """3D 생성 제어 옵션들"""
    controls = {}
    
    with st.expander("3D 설정"):
        col1, col2 = st.columns(2)
        
        with col1:
            texture_resolution = st.selectbox(
                "텍스처 해상도",
                options=["512", "1024", "2048"],
                index=1,
                help="높은 해상도는 더 세밀한 텍스처를 제공하지만 파일 크기가 커집니다."
            )
            
            foreground_ratio = st.slider(
                "전경 비율",
                min_value=0.1,
                max_value=2.0,
                value=0.85,
                step=0.05,
                help="객체가 프레임에서 차지하는 비율을 조절합니다."
            )
        
        with col2:
            remesh = st.selectbox(
                "리메시 타입",
                options=["none", "quad", "triangle"],
                index=0,
                help="메시 구조를 최적화합니다. DCC 도구 사용 시 quad 권장."
            )
            
            vertex_count = st.number_input(
                "정점 개수 (-1 = 제한없음)",
                min_value=-1,
                max_value=20000,
                value=-1,
                help="메시의 복잡도를 제어합니다."
            )
    
    controls["texture_resolution"] = texture_resolution
    controls["foreground_ratio"] = foreground_ratio
    controls["remesh"] = remesh if remesh != "none" else None
    if vertex_count > 0:
        controls["vertex_count"] = vertex_count
    
    return controls


def create_style_transfer_controls() -> Dict[str, Any]:
    """스타일 전송 제어 옵션들"""
    controls = {}
    
    with st.expander("스타일 전송 설정"):
        col1, col2 = st.columns(2)
        
        with col1:
            controls["style_strength"] = st.slider(
                "스타일 강도",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.1,
                help="스타일 이미지의 영향력을 조절합니다."
            )
            
            controls["composition_fidelity"] = st.slider(
                "구성 충실도",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.1,
                help="원본 이미지의 구조를 얼마나 보존할지 결정합니다."
            )
        
        with col2:
            controls["change_strength"] = st.slider(
                "변화 강도",
                min_value=0.1,
                max_value=1.0,
                value=0.9,
                step=0.1,
                help="입력 이미지를 얼마나 변화시킬지 조절합니다."
            )
    
    return controls


def show_api_response_info(response):
    """API 응답 정보 표시"""
    if response.status_code == 200:
        st.success("✅ 생성 완료!")
        
        # 응답 헤더 정보
        with st.expander("응답 정보"):
            st.write(f"**상태 코드**: {response.status_code}")
            st.write(f"**콘텐츠 타입**: {response.headers.get('content-type', 'N/A')}")
            if 'content-length' in response.headers:
                size = int(response.headers['content-length'])
                st.write(f"**파일 크기**: {size:,} 바이트")
    
    elif response.status_code == 202:
        st.info("⏳ 생성 중입니다. 잠시만 기다려주세요...")
    
    else:
        st.error(f"❌ API 오류 (코드: {response.status_code})")
        try:
            error_data = response.json()
            st.error(f"오류 메시지: {error_data}")
        except:
            st.error(f"응답 내용: {response.text}")


def show_api_request_debug(params, has_image=False):
    """API 요청 디버그 정보 표시"""
    with st.expander("🔍 API 요청 디버그 정보"):
        st.write("**전송되는 파라미터:**")
        debug_params = params.copy()
        
        # 민감한 정보는 마스킹
        if 'prompt' in debug_params:
            st.write(f"- **prompt**: {debug_params['prompt'][:100]}{'...' if len(debug_params['prompt']) > 100 else ''}")
        
        if 'negative_prompt' in debug_params:
            st.write(f"- **negative_prompt**: {debug_params['negative_prompt'][:50]}{'...' if len(debug_params['negative_prompt']) > 50 else ''}")
        
        # 다른 파라미터들
        for key, value in debug_params.items():
            if key not in ['prompt', 'negative_prompt'] and value is not None:
                st.write(f"- **{key}**: {value}")
        
        if has_image:
            st.write("- **image**: ✅ 이미지 파일 첨부됨")
        else:
            st.write("- **image**: ❌ 이미지 없음")
        
        st.write(f"**총 파라미터 개수**: {len([k for k, v in debug_params.items() if v is not None])}")


def create_generation_history():
    """생성 히스토리 관리"""
    if "generation_history" not in st.session_state:
        st.session_state.generation_history = []
    
    with st.sidebar:
        st.subheader("🕒 생성 히스토리")
        
        if st.session_state.generation_history:
            for i, item in enumerate(reversed(st.session_state.generation_history[-10:])):
                with st.expander(f"{item['type']} - {item['timestamp'][:19]}"):
                    st.write(f"**프롬프트**: {item['prompt'][:100]}...")
                    if st.button(f"재사용", key=f"reuse_{i}"):
                        return item
        else:
            st.write("아직 생성 히스토리가 없습니다.")
    
    return None


def add_to_history(generation_type: str, prompt: str, params: Dict[str, Any]):
    """히스토리에 항목 추가"""
    import datetime
    
    if "generation_history" not in st.session_state:
        st.session_state.generation_history = []
    
    item = {
        "type": generation_type,
        "prompt": prompt,
        "params": params,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    st.session_state.generation_history.append(item)
    
    # 최대 50개 항목만 유지
    if len(st.session_state.generation_history) > 50:
        st.session_state.generation_history.pop(0)