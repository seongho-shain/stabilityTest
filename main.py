"""
Stability AI 종합 테스트 애플리케이션
모든 Stability AI API 기능을 테스트할 수 있는 통합 Streamlit 웹 애플리케이션
"""

import streamlit as st
import io
import datetime
from utils.api_client import get_api_client
from utils.file_handler import (
    process_uploaded_image, process_uploaded_audio, display_image_with_info,
    create_download_button, validate_image_file, validate_audio_file
)
from utils.ui_components import (
    create_prompt_input, create_negative_prompt_input, create_basic_image_controls,
    create_advanced_controls, create_audio_controls, create_3d_controls,
    create_style_transfer_controls, show_api_response_info, create_generation_history,
    add_to_history, create_generation_mode_selector, show_api_request_debug
)

# 페이지 설정
st.set_page_config(
    page_title="Stability AI 테스트 플랫폼",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🎨 Stability AI 종합 테스트 플랫폼</h1>
    <p>모든 Stability AI API 기능을 하나의 플랫폼에서 테스트해보세요!</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 네비게이션
st.sidebar.title("🔧 기능 선택")

# API 상태 확인
with st.sidebar:
    try:
        client = get_api_client()
        st.success("✅ API 연결 성공")
    except Exception as e:
        st.error("❌ API 연결 실패")
        st.error("💡 .env 파일의 API 키를 확인해주세요")
        st.stop()

main_category = st.sidebar.selectbox(
    "카테고리 선택",
    [
        "🎨 이미지 생성",
        "🎛️ 이미지 제어/편집", 
        "🎵 오디오 생성",
        "🎭 3D 모델 생성"
    ]
)

# 도움말 정보
with st.sidebar.expander("💡 사용 팁"):
    st.markdown("""
    **프롬프트 작성 팁:**
    - 구체적이고 상세한 설명
    - 스타일, 색상, 분위기 명시
    - 네거티브 프롬프트 활용
    
    **파일 업로드:**
    - 이미지: 최대 50MB, 64px 이상
    - 오디오: MP3/WAV, 최대 50MB
    
    **3D 변환:**
    - 단순한 배경의 명확한 객체
    - GLB 파일로 출력
    """)

# 생성 히스토리
history_item = create_generation_history()

# 메인 컨텐츠 영역
if main_category == "🎨 이미지 생성":
    st.header("🎨 이미지 생성")
    
    # 하위 기능 선택
    sub_function = st.selectbox(
        "이미지 생성 방식 선택",
        [
            "Stable Image Core (기본)",
            "Stable Diffusion 3.5 (고급)",
            "Stable Image Ultra (최고급)"
        ]
    )
    
    # 기능 설명
    if "Core" in sub_function:
        st.info("⚡ **Stable Image Core**: 빠르고 안정적인 기본 이미지 생성 (텍스트→이미지만 지원) (3 크레딧)")
    elif "3.5" in sub_function:
        st.info("🎯 **Stable Diffusion 3.5**: 고급 품질과 프롬프트 준수도, 텍스트→이미지 & 이미지→이미지 지원 (3.5-6.5 크레딧)")
    else:
        st.info("⭐ **Stable Image Ultra**: 최고급 품질, 타이포그래피와 조명 최적화, 참조 이미지 지원 (8 크레딧)")
    
    # 생성 모드 선택
    col_mode1, col_mode2 = st.columns([1, 2])
    
    with col_mode1:
        if "3.5" in sub_function:
            generation_mode = create_generation_mode_selector("sd3.5")
        elif "Ultra" in sub_function:
            generation_mode = create_generation_mode_selector("ultra")
        else:
            generation_mode = create_generation_mode_selector("core")
    
    with col_mode2:
        if "Image" in generation_mode and generation_mode != "Text-to-Image":
            st.info("💡 Image-to-Image 모드: 입력 이미지를 프롬프트에 따라 변형합니다.")
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = create_prompt_input("프롬프트 입력", "생성하고 싶은 이미지를 상세히 설명해주세요.")
        negative_prompt = create_negative_prompt_input()
        
        # 프롬프트 미리보기 (디버그용)
        if prompt.strip():
            with st.expander("📝 입력된 프롬프트 미리보기"):
                st.write(f"**프롬프트 길이**: {len(prompt)} 문자")
                st.write(f"**프롬프트 내용**: {prompt}")
                if negative_prompt.strip():
                    st.write(f"**네거티브 프롬프트**: {negative_prompt}")
        
        # Image-to-Image 모드에서 이미지 업로드
        uploaded_input_image = None
        input_image_data = None
        
        if "Image" in generation_mode and generation_mode != "Text-to-Image":
            st.subheader("🖼️ 입력 이미지")
            if "3.5" in sub_function:
                uploaded_input_image = st.file_uploader(
                    "변형할 이미지 업로드",
                    type=["png", "jpg", "jpeg", "webp"],
                    help="이 이미지를 프롬프트에 따라 변형합니다."
                )
            else:  # Ultra
                uploaded_input_image = st.file_uploader(
                    "참조 이미지 업로드",
                    type=["png", "jpg", "jpeg", "webp"],
                    help="이 이미지를 참조하여 새로운 이미지를 생성합니다."
                )
            
            if uploaded_input_image:
                input_image_data = process_uploaded_image(uploaded_input_image)
                if input_image_data:
                    st.image(uploaded_input_image, caption="입력 이미지", width=300)
    
    with col2:
        # 종횡비는 text-to-image 모드에서만 표시 (SD3.5)
        show_aspect = not ("3.5" in sub_function and "Image-to-Image" in generation_mode)
        basic_controls = create_basic_image_controls(show_aspect_ratio=show_aspect)
        
        # Image-to-Image 모드에서 strength 슬라이더
        if "Image" in generation_mode and generation_mode != "Text-to-Image":
            strength = st.slider(
                "변형 강도" if "3.5" in sub_function else "참조 이미지 영향도",
                0.0, 1.0, 0.8 if "3.5" in sub_function else 0.5, 0.1,
                help="높을수록 입력 이미지에서 더 많이 변화합니다."
            )
            basic_controls["strength"] = strength
        
        # 모델별 고급 설정
        if "3.5" in sub_function:
            advanced_controls = create_advanced_controls(show_cfg_scale=True)
            model_choice = st.selectbox(
                "SD3.5 모델 선택",
                ["sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium"],
                help="Large: 최고 품질, Turbo: 빠른 생성, Medium: 균형"
            )
            advanced_controls["model"] = model_choice
            
            # SD3.5에서 모드 설정
            if "Image-to-Image" in generation_mode:
                advanced_controls["mode"] = "image-to-image"
            else:
                advanced_controls["mode"] = "text-to-image"
        
        elif "Ultra" in sub_function:
            advanced_controls = create_advanced_controls(show_cfg_scale=False)
        else:
            advanced_controls = create_advanced_controls(show_cfg_scale=False, show_steps=False)
    
    # 생성 버튼
    if st.button("🎨 이미지 생성", type="primary", use_container_width=True):
        if not prompt.strip():
            st.error("프롬프트를 입력해주세요.")
        elif "Image" in generation_mode and generation_mode != "Text-to-Image" and not uploaded_input_image:
            st.error("Image-to-Image 모드에서는 입력 이미지가 필요합니다.")
        else:
            with st.spinner("이미지 생성 중..."):
                try:
                    # 파라미터 준비
                    params = {**basic_controls, **advanced_controls}
                    if negative_prompt.strip():
                        params["negative_prompt"] = negative_prompt
                    
                    # 디버그 정보 표시
                    has_input_image = (input_image_data is not None)
                    show_api_request_debug(params, has_input_image)
                    
                    # API 호출
                    if "Core" in sub_function:
                        response = client.generate_core_image(prompt, **params)
                        api_type = "Stable Image Core"
                    
                    elif "3.5" in sub_function:
                        if "Image-to-Image" in generation_mode:
                            response = client.generate_sd35_image(prompt, input_image_data, **params)
                            api_type = "Stable Diffusion 3.5 (Image-to-Image)"
                        else:
                            response = client.generate_sd35_image(prompt, **params)
                            api_type = "Stable Diffusion 3.5 (Text-to-Image)"
                    
                    else:  # Ultra
                        if "Text+Image" in generation_mode:
                            response = client.generate_ultra_image(prompt, input_image_data, **params)
                            api_type = "Stable Image Ultra (Text+Image-to-Image)"
                        else:
                            response = client.generate_ultra_image(prompt, **params)
                            api_type = "Stable Image Ultra (Text-to-Image)"
                    
                    show_api_response_info(response)
                    
                    if response.status_code == 200:
                        # 이미지 표시
                        image = display_image_with_info(response.content, f"{api_type} 생성 이미지")
                        
                        # 다운로드 버튼
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{api_type.replace(' ', '_').replace('(', '').replace(')', '')}_{timestamp}.{params.get('output_format', 'png')}"
                        create_download_button(
                            response.content,
                            filename,
                            f"image/{params.get('output_format', 'png')}",
                            f"💾 {filename} 다운로드"
                        )
                        
                        # 히스토리에 추가
                        add_to_history(api_type, prompt, params)
                
                except Exception as e:
                    st.error(f"이미지 생성 중 오류가 발생했습니다: {str(e)}")

elif main_category == "🎛️ 이미지 제어/편집":
    st.header("🎛️ 이미지 제어/편집")
    
    sub_function = st.selectbox(
        "제어/편집 방식 선택",
        [
            "Sketch (스케치 → 이미지)",
            "Structure (구조 제어)",
            "Style Guide (스타일 가이드)",
            "Style Transfer (스타일 전송)"
        ]
    )
    
    # 기능 설명
    if "Sketch" in sub_function:
        st.info("✏️ **Sketch**: 스케치나 선화를 상세한 이미지로 변환 (3 크레딧)")
    elif "Structure" in sub_function:
        st.info("🏗️ **Structure**: 구조를 보존하며 새로운 이미지 생성 (3 크레딧)")
    elif "Style Guide" in sub_function:
        st.info("🎨 **Style Guide**: 참조 이미지의 스타일을 적용하여 생성 (4 크레딧)")
    else:
        st.info("🔄 **Style Transfer**: 두 이미지의 스타일을 조합 (8 크레딧)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if sub_function != "Style Transfer (스타일 전송)":
            prompt = create_prompt_input("프롬프트 입력")
            negative_prompt = create_negative_prompt_input()
        
        # 파일 업로드
        if sub_function == "Style Transfer (스타일 전송)":
            st.subheader("이미지 업로드")
            col_upload1, col_upload2 = st.columns(2)
            
            with col_upload1:
                st.write("**원본 이미지**")
                init_image = st.file_uploader("변환할 이미지", type=["png", "jpg", "jpeg", "webp"], key="init")
                if init_image:
                    st.image(init_image, caption="원본 이미지", width=200)
            
            with col_upload2:
                st.write("**스타일 이미지**")
                style_image = st.file_uploader("스타일 참조 이미지", type=["png", "jpg", "jpeg", "webp"], key="style")
                if style_image:
                    st.image(style_image, caption="스타일 이미지", width=200)
        else:
            uploaded_image = st.file_uploader(
                "입력 이미지 업로드",
                type=["png", "jpg", "jpeg", "webp"],
                help="제어/편집할 기준 이미지를 업로드하세요."
            )
            if uploaded_image:
                st.image(uploaded_image, caption="입력 이미지", width=300)
    
    with col2:
        if sub_function == "Style Transfer (스타일 전송)":
            basic_controls = {"output_format": "webp", "seed": None}
            advanced_controls = create_style_transfer_controls()
        else:
            basic_controls = create_basic_image_controls()
            
            if sub_function == "Style Guide (스타일 가이드)":
                advanced_controls = create_advanced_controls(show_control_strength=False)
                fidelity = st.slider("스타일 충실도", 0.0, 1.0, 0.5, 0.1, help="높을수록 참조 스타일을 더 정확히 따릅니다")
                advanced_controls["fidelity"] = fidelity
            else:
                advanced_controls = create_advanced_controls(show_control_strength=True)
    
    # 생성 버튼
    if st.button("🎛️ 이미지 처리", type="primary", use_container_width=True):
        # 입력 검증
        if sub_function == "Style Transfer (스타일 전송)":
            if not init_image or not style_image:
                st.error("원본 이미지와 스타일 이미지를 모두 업로드해주세요.")
            else:
                with st.spinner("스타일 전송 중..."):
                    try:
                        init_data = process_uploaded_image(init_image)
                        style_data = process_uploaded_image(style_image)
                        
                        if init_data and style_data:
                            params = {**basic_controls, **advanced_controls}
                            response = client.style_transfer(init_data, style_data, **params)
                            
                            show_api_response_info(response)
                            
                            if response.status_code == 200:
                                display_image_with_info(response.content, "스타일 전송 결과")
                                
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"style_transfer_{timestamp}.{params.get('output_format', 'webp')}"
                                create_download_button(
                                    response.content,
                                    filename,
                                    f"image/{params.get('output_format', 'webp')}",
                                    f"💾 {filename} 다운로드"
                                )
                                
                                add_to_history("Style Transfer", "Style transfer", params)
                    
                    except Exception as e:
                        st.error(f"스타일 전송 중 오류: {str(e)}")
        
        else:
            if not uploaded_image:
                st.error("입력 이미지를 업로드해주세요.")
            elif not prompt.strip():
                st.error("프롬프트를 입력해주세요.")
            else:
                with st.spinner(f"{sub_function} 처리 중..."):
                    try:
                        image_data = process_uploaded_image(uploaded_image)
                        
                        if image_data:
                            params = {**basic_controls, **advanced_controls}
                            if negative_prompt.strip():
                                params["negative_prompt"] = negative_prompt
                            
                            # API 호출
                            if "Sketch" in sub_function:
                                response = client.sketch_to_image(prompt, image_data, **params)
                                api_type = "Sketch ControlNet"
                            elif "Structure" in sub_function:
                                response = client.structure_control(prompt, image_data, **params)
                                api_type = "Structure ControlNet"
                            else:  # Style Guide
                                response = client.style_guide(prompt, image_data, **params)
                                api_type = "Style Guide ControlNet"
                            
                            show_api_response_info(response)
                            
                            if response.status_code == 200:
                                display_image_with_info(response.content, f"{api_type} 결과")
                                
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"{api_type.replace(' ', '_')}_{timestamp}.{params.get('output_format', 'png')}"
                                create_download_button(
                                    response.content,
                                    filename,
                                    f"image/{params.get('output_format', 'png')}",
                                    f"💾 {filename} 다운로드"
                                )
                                
                                add_to_history(api_type, prompt, params)
                    
                    except Exception as e:
                        st.error(f"이미지 처리 중 오류: {str(e)}")

elif main_category == "🎵 오디오 생성":
    st.header("🎵 오디오 생성")
    
    sub_function = st.selectbox(
        "오디오 생성 방식 선택",
        [
            "Text-to-Audio (텍스트 → 오디오)",
            "Audio-to-Audio (오디오 변환)"
        ]
    )
    
    # 기능 설명
    if "Text-to-Audio" in sub_function:
        st.info("🎼 **Text-to-Audio**: 텍스트 설명으로 음악이나 효과음 생성 (9+0.06×스텝 크레딧)")
    else:
        st.info("🔄 **Audio-to-Audio**: 기존 오디오를 다른 스타일로 변환 (9+0.06×스텝 크레딧)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = create_prompt_input(
            "오디오 프롬프트",
            "생성하고 싶은 음악이나 소리를 상세히 설명해주세요. (예: 잔잔한 피아노 멜로디, 비 오는 소리 등)"
        )
        
        if sub_function == "Audio-to-Audio (오디오 변환)":
            uploaded_audio = st.file_uploader(
                "변환할 오디오 파일 업로드",
                type=["mp3", "wav"],
                help="변환할 기준 오디오 파일을 업로드하세요."
            )
            
            if uploaded_audio:
                st.audio(uploaded_audio, format=uploaded_audio.type)
                
                # 오디오 변환 전용 설정
                strength = st.slider(
                    "원본 오디오 영향도",
                    0.0, 1.0, 1.0, 0.1,
                    help="0에 가까우면 프롬프트 중심, 1에 가까우면 원본 오디오 중심"
                )
                
                negative_prompt = st.text_area(
                    "네거티브 프롬프트 (선택사항)",
                    help="생성하지 않을 음악/소리 요소를 입력하세요."
                )
    
    with col2:
        audio_controls = create_audio_controls()
    
    # 생성 버튼
    if st.button("🎵 오디오 생성", type="primary", use_container_width=True):
        if not prompt.strip():
            st.error("오디오 프롬프트를 입력해주세요.")
        elif sub_function == "Audio-to-Audio (오디오 변환)" and not uploaded_audio:
            st.error("변환할 오디오 파일을 업로드해주세요.")
        else:
            with st.spinner("오디오 생성 중... (시간이 좀 걸릴 수 있습니다)"):
                try:
                    params = audio_controls.copy()
                    
                    if sub_function == "Text-to-Audio (텍스트 → 오디오)":
                        response = client.text_to_audio(prompt, **params)
                        api_type = "Text-to-Audio"
                    
                    else:  # Audio-to-Audio
                        audio_data = process_uploaded_audio(uploaded_audio)
                        if audio_data:
                            params["strength"] = strength
                            if negative_prompt.strip():
                                params["negative_prompt"] = negative_prompt
                            
                            response = client.audio_to_audio(prompt, audio_data, **params)
                            api_type = "Audio-to-Audio"
                        else:
                            st.error("오디오 파일 처리에 실패했습니다.")
                            st.stop()
                    
                    show_api_response_info(response)
                    
                    if response.status_code == 200:
                        # 오디오 재생
                        st.success("✅ 오디오 생성 완료!")
                        st.audio(response.content, format=f"audio/{params['output_format']}")
                        
                        # 다운로드 버튼
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{api_type.replace('-', '_')}_{timestamp}.{params['output_format']}"
                        create_download_button(
                            response.content,
                            filename,
                            f"audio/{params['output_format']}",
                            f"💾 {filename} 다운로드"
                        )
                        
                        # 오디오 정보
                        with st.expander("오디오 정보"):
                            st.write(f"**길이**: {params['duration']}초")
                            st.write(f"**형식**: {params['output_format'].upper()}")
                            st.write(f"**파일 크기**: {len(response.content):,} 바이트")
                            st.write(f"**샘플링 스텝**: {params['steps']}")
                        
                        add_to_history(api_type, prompt, params)
                
                except Exception as e:
                    st.error(f"오디오 생성 중 오류: {str(e)}")

elif main_category == "🎭 3D 모델 생성":
    st.header("🎭 3D 모델 생성")
    
    sub_function = st.selectbox(
        "3D 생성 방식 선택",
        [
            "Stable Fast 3D (빠른 생성)",
            "Stable Point Aware 3D (고품질)"
        ]
    )
    
    # 기능 설명
    if "Fast 3D" in sub_function:
        st.info("⚡ **Stable Fast 3D**: 빠른 2D→3D 변환, 게임과 실시간 앱에 최적화 (2 크레딧)")
    else:
        st.info("⭐ **Stable Point Aware 3D**: 고품질 3D 모델, 상세한 뒷면 복원 (4 크레딧)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("입력 이미지")
        uploaded_image = st.file_uploader(
            "3D로 변환할 2D 이미지 업로드",
            type=["png", "jpg", "jpeg", "webp"],
            help="명확한 객체가 있는 이미지를 업로드하세요. 배경이 단순할수록 좋은 결과를 얻을 수 있습니다."
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="입력 이미지", width=400)
            
            # 이미지 정보 표시
            is_valid, message = validate_image_file(uploaded_image)
            if is_valid:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        controls_3d = create_3d_controls()
        
        # Point Aware 3D 전용 설정
        if "Point Aware" in sub_function:
            with st.expander("Point Aware 3D 전용 설정"):
                guidance_scale = st.slider(
                    "가이던스 스케일",
                    1.0, 10.0, 3.0, 0.5,
                    help="높을수록 더 정확하지만 아티팩트가 생길 수 있습니다."
                )
                controls_3d["guidance_scale"] = guidance_scale
                
                target_type = st.selectbox(
                    "타겟 타입",
                    ["none", "vertex", "face"],
                    help="메시 최적화 방식을 선택합니다."
                )
                if target_type != "none":
                    controls_3d["target_type"] = target_type
                    
                    target_count = st.number_input(
                        "타겟 개수",
                        100, 20000, 1000,
                        help="정점/면의 개수를 제한합니다."
                    )
                    controls_3d["target_count"] = target_count
    
    # 생성 버튼
    if st.button("🎭 3D 모델 생성", type="primary", use_container_width=True):
        if not uploaded_image:
            st.error("3D로 변환할 이미지를 업로드해주세요.")
        else:
            with st.spinner("3D 모델 생성 중... (1-2분 정도 소요됩니다)"):
                try:
                    image_data = process_uploaded_image(uploaded_image)
                    
                    if image_data:
                        # API 호출
                        if "Fast 3D" in sub_function:
                            response = client.fast_3d(image_data, **controls_3d)
                            api_type = "Stable Fast 3D"
                        else:  # Point Aware 3D
                            response = client.point_aware_3d(image_data, **controls_3d)
                            api_type = "Stable Point Aware 3D"
                        
                        show_api_response_info(response)
                        
                        if response.status_code == 200:
                            st.success("✅ 3D 모델 생성 완료!")
                            
                            # 3D 모델 다운로드
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{api_type.replace(' ', '_')}_{timestamp}.glb"
                            create_download_button(
                                response.content,
                                filename,
                                "model/gltf-binary",
                                f"💾 {filename} 다운로드"
                            )
                            
                            # 3D 모델 정보
                            with st.expander("3D 모델 정보"):
                                st.write(f"**파일 형식**: GLB (Binary glTF)")
                                st.write(f"**파일 크기**: {len(response.content):,} 바이트")
                                st.write(f"**텍스처 해상도**: {controls_3d.get('texture_resolution', '1024')}px")
                                if controls_3d.get("remesh"):
                                    st.write(f"**리메시**: {controls_3d['remesh']}")
                                if "Point Aware" in sub_function:
                                    st.write(f"**가이던스 스케일**: {controls_3d.get('guidance_scale', 3.0)}")
                            
                            st.info("💡 생성된 GLB 파일은 Blender, Unity, Unreal Engine 등에서 사용할 수 있습니다.")
                            
                            add_to_history(api_type, f"3D conversion from uploaded image", controls_3d)
                
                except Exception as e:
                    st.error(f"3D 모델 생성 중 오류: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div class="info-box">
    <h4>🔧 사용 가능한 기능들</h4>
    <ul>
        <li><strong>이미지 생성</strong>: Core, SD3.5, Ultra 모델로 텍스트→이미지</li>
        <li><strong>이미지 제어</strong>: Sketch, Structure, Style Guide, Style Transfer</li>
        <li><strong>오디오 생성</strong>: 텍스트→오디오, 오디오→오디오 변환</li>
        <li><strong>3D 모델</strong>: Fast 3D, Point Aware 3D로 2D→3D 변환</li>
    </ul>
    <p><em>💡 생성 히스토리는 사이드바에서 확인하고 재사용할 수 있습니다.</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align: center; margin-top: 2rem;'>
        <p>🎨 <strong>Stability AI 종합 테스트 플랫폼</strong> | 
        모든 기능을 한 곳에서 테스트하세요!</p>
        <p><em>API 키는 .env 파일에서 안전하게 관리됩니다.</em></p>
    </div>
    """,
    unsafe_allow_html=True
)