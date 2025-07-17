#!/usr/bin/env python3
"""
Stability AI 테스트 애플리케이션 실행 스크립트
"""

import os
import sys
import subprocess

def check_requirements():
    """필요한 패키지들이 설치되어 있는지 확인"""
    required_packages = [
        'streamlit',
        'requests', 
        'python-dotenv',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지들이 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """환경 파일이 올바르게 설정되어 있는지 확인"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ .env 파일이 없습니다.")
        print("Stability AI API 키를 설정해주세요.")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    if "your-api-key-here" in content:
        print("❌ .env 파일에 실제 API 키를 설정해주세요.")
        print("STABILITY_API_KEY=your-actual-api-key")
        return False
    
    if "STABILITY_API_KEY=" not in content:
        print("❌ .env 파일에 STABILITY_API_KEY가 설정되지 않았습니다.")
        return False
    
    return True

def run_streamlit():
    """Streamlit 애플리케이션 실행"""
    try:
        print("🚀 Stability AI 테스트 플랫폼을 시작합니다...")
        print("📖 브라우저에서 http://localhost:8501 이 자동으로 열립니다.")
        print("🛑 종료하려면 Ctrl+C를 누르세요.")
        print("-" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--theme.base", "light",
            "--theme.primaryColor", "#667eea",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit 실행 중 오류가 발생했습니다: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 애플리케이션을 종료합니다.")
        return True

def main():
    """메인 실행 함수"""
    print("🎨 Stability AI 종합 테스트 플랫폼")
    print("=" * 50)
    
    # 필수 패키지 확인
    if not check_requirements():
        sys.exit(1)
    print("✅ 필요한 패키지들이 모두 설치되어 있습니다.")
    
    # 환경 파일 확인
    if not check_env_file():
        sys.exit(1)
    print("✅ 환경 설정이 올바르게 되어 있습니다.")
    
    # Streamlit 실행
    run_streamlit()

if __name__ == "__main__":
    main()