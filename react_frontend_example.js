/**
 * React 프론트엔드 예제
 * Stability AI 이미지 생성 인터페이스
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60초 타임아웃
});

// 상수들
const OUTPUT_FORMATS = ['png', 'jpeg', 'webp'];
const ASPECT_RATIOS = [
  { label: '정사각형 (1:1)', value: '1:1' },
  { label: '가로 (16:9)', value: '16:9' },
  { label: '세로 (9:16)', value: '9:16' },
  { label: '가로 (3:2)', value: '3:2' },
  { label: '세로 (2:3)', value: '2:3' },
  { label: '가로 (4:3)', value: '4:3' },
  { label: '세로 (3:4)', value: '3:4' },
];

const STYLE_PRESETS = [
  { label: '기본값', value: '' },
  { label: '사진', value: 'photographic' },
  { label: '애니메이션', value: 'anime' },
  { label: '디지털 아트', value: 'digital-art' },
  { label: '3D 모델', value: '3d-model' },
  { label: '픽셀 아트', value: 'pixel-art' },
  { label: '영화적', value: 'cinematic' },
  { label: '판타지', value: 'fantasy-art' },
  { label: '일러스트', value: 'illustration' },
];

const SD35_MODELS = [
  { label: 'Large (최고 품질)', value: 'sd3.5-large' },
  { label: 'Large Turbo (빠른 생성)', value: 'sd3.5-large-turbo' },
  { label: 'Medium (균형)', value: 'sd3.5-medium' },
];

// 파일 검증 함수
const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
  const maxSize = 50 * 1024 * 1024; // 50MB

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: '지원되지 않는 파일 형식입니다. (JPEG, PNG, WebP만 지원)' };
  }

  if (file.size > maxSize) {
    return { valid: false, error: '파일 크기가 50MB를 초과합니다.' };
  }

  return { valid: true };
};

// 로딩 스피너 컴포넌트
const LoadingSpinner = () => (
  <div className="loading-spinner">
    <div className="spinner"></div>
    <p>이미지 생성 중...</p>
  </div>
);

// 에러 표시 컴포넌트
const ErrorDisplay = ({ error, onClose }) => (
  <div className="error-display">
    <div className="error-content">
      <h3>오류 발생</h3>
      <p>{error}</p>
      <button onClick={onClose}>닫기</button>
    </div>
  </div>
);

// 파일 업로드 컴포넌트
const FileUpload = ({ onFileSelect, accept = "image/*", label = "이미지 업로드" }) => {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  return (
    <div 
      className={`file-upload ${dragOver ? 'drag-over' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        accept={accept}
        onChange={(e) => onFileSelect(e.target.files[0])}
        style={{ display: 'none' }}
        id="file-input"
      />
      <label htmlFor="file-input" className="file-upload-label">
        <div className="upload-content">
          <p>{label}</p>
          <small>드래그 앤 드롭 또는 클릭하여 선택</small>
        </div>
      </label>
    </div>
  );
};

// 메인 이미지 생성 컴포넌트
const ImageGenerationApp = () => {
  // 상태 관리
  const [activeTab, setActiveTab] = useState('generation');
  const [generationType, setGenerationType] = useState('core');
  const [generationMode, setGenerationMode] = useState('text-to-image');
  
  // 폼 데이터
  const [formData, setFormData] = useState({
    prompt: '',
    negative_prompt: '',
    output_format: 'png',
    aspect_ratio: '1:1',
    style_preset: '',
    seed: '',
    // SD3.5 전용
    model: 'sd3.5-large',
    strength: 0.8,
    // 제어 전용
    control_strength: 0.7,
    fidelity: 0.5,
  });

  // 파일 관리
  const [uploadedImage, setUploadedImage] = useState(null);
  const [styleImage, setStyleImage] = useState(null);
  
  // UI 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedImage, setGeneratedImage] = useState(null);

  // 폼 데이터 업데이트
  const updateFormData = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  // 이미지 생성 API 호출
  const generateImage = async () => {
    try {
      setLoading(true);
      setError(null);
      setGeneratedImage(null);

      const formDataToSend = new FormData();
      
      // 기본 데이터 추가
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          formDataToSend.append(key, formData[key]);
        }
      });

      // 모드에 따른 파일 추가
      if (generationMode === 'image-to-image' && uploadedImage) {
        formDataToSend.append('image', uploadedImage);
      }

      // API 엔드포인트 결정
      let endpoint;
      switch (generationType) {
        case 'core':
          endpoint = '/api/image/generate/core';
          break;
        case 'sd35':
          endpoint = '/api/image/generate/sd35';
          formDataToSend.append('mode', generationMode);
          break;
        case 'ultra':
          endpoint = '/api/image/generate/ultra';
          break;
        default:
          throw new Error('알 수 없는 생성 타입');
      }

      const response = await api.post(endpoint, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      // 생성된 이미지 표시
      const imageUrl = URL.createObjectURL(response.data);
      setGeneratedImage(imageUrl);

    } catch (err) {
      console.error('이미지 생성 오류:', err);
      setError(err.response?.data?.detail || '이미지 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 이미지 제어 API 호출
  const controlImage = async (controlType) => {
    try {
      setLoading(true);
      setError(null);
      setGeneratedImage(null);

      if (!uploadedImage) {
        throw new Error('입력 이미지를 업로드해주세요.');
      }

      const formDataToSend = new FormData();
      
      // 기본 데이터 추가
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          formDataToSend.append(key, formData[key]);
        }
      });

      formDataToSend.append('image', uploadedImage);

      // 스타일 전송의 경우 추가 이미지
      if (controlType === 'style-transfer' && styleImage) {
        formDataToSend.append('style_image', styleImage);
        formDataToSend.append('init_image', uploadedImage);
      }

      const response = await api.post(`/api/image/control/${controlType}`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const imageUrl = URL.createObjectURL(response.data);
      setGeneratedImage(imageUrl);

    } catch (err) {
      console.error('이미지 제어 오류:', err);
      setError(err.response?.data?.detail || '이미지 처리 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 파일 선택 핸들러
  const handleImageSelect = (file) => {
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }
    setUploadedImage(file);
    setError(null);
  };

  const handleStyleImageSelect = (file) => {
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }
    setStyleImage(file);
    setError(null);
  };

  return (
    <div className="app-container">
      <header>
        <h1>🎨 Stability AI 이미지 생성</h1>
        <nav>
          <button 
            className={activeTab === 'generation' ? 'active' : ''}
            onClick={() => setActiveTab('generation')}
          >
            이미지 생성
          </button>
          <button 
            className={activeTab === 'control' ? 'active' : ''}
            onClick={() => setActiveTab('control')}
          >
            이미지 제어/편집
          </button>
        </nav>
      </header>

      <main>
        {activeTab === 'generation' && (
          <div className="generation-panel">
            <div className="controls">
              {/* 생성 타입 선택 */}
              <div className="control-group">
                <label>생성 모델</label>
                <select 
                  value={generationType} 
                  onChange={(e) => setGenerationType(e.target.value)}
                >
                  <option value="core">Stable Image Core (기본)</option>
                  <option value="sd35">Stable Diffusion 3.5 (고급)</option>
                  <option value="ultra">Stable Image Ultra (최고급)</option>
                </select>
              </div>

              {/* SD3.5 모드 선택 */}
              {generationType === 'sd35' && (
                <div className="control-group">
                  <label>생성 모드</label>
                  <select 
                    value={generationMode} 
                    onChange={(e) => setGenerationMode(e.target.value)}
                  >
                    <option value="text-to-image">텍스트 → 이미지</option>
                    <option value="image-to-image">이미지 → 이미지</option>
                  </select>
                </div>
              )}

              {/* 프롬프트 입력 */}
              <div className="control-group">
                <label>프롬프트</label>
                <textarea
                  value={formData.prompt}
                  onChange={(e) => updateFormData('prompt', e.target.value)}
                  placeholder="생성하고 싶은 이미지를 상세히 설명해주세요..."
                  rows={4}
                />
              </div>

              <div className="control-group">
                <label>네거티브 프롬프트 (선택사항)</label>
                <textarea
                  value={formData.negative_prompt}
                  onChange={(e) => updateFormData('negative_prompt', e.target.value)}
                  placeholder="생성하지 않을 요소들..."
                  rows={2}
                />
              </div>

              {/* 이미지 업로드 (Image-to-Image 모드) */}
              {generationMode === 'image-to-image' && (
                <div className="control-group">
                  <label>입력 이미지</label>
                  <FileUpload onFileSelect={handleImageSelect} />
                  {uploadedImage && (
                    <div className="uploaded-image-preview">
                      <img 
                        src={URL.createObjectURL(uploadedImage)} 
                        alt="업로드된 이미지" 
                        style={{ maxWidth: '200px', maxHeight: '200px' }}
                      />
                      <p>{uploadedImage.name}</p>
                    </div>
                  )}
                </div>
              )}

              {/* 기본 설정들 */}
              <div className="basic-controls">
                <div className="control-row">
                  <div className="control-group">
                    <label>출력 형식</label>
                    <select 
                      value={formData.output_format}
                      onChange={(e) => updateFormData('output_format', e.target.value)}
                    >
                      {OUTPUT_FORMATS.map(format => (
                        <option key={format} value={format}>{format.toUpperCase()}</option>
                      ))}
                    </select>
                  </div>

                  {/* 종횡비 (text-to-image 모드에서만) */}
                  {(generationType !== 'sd35' || generationMode !== 'image-to-image') && (
                    <div className="control-group">
                      <label>이미지 비율</label>
                      <select 
                        value={formData.aspect_ratio}
                        onChange={(e) => updateFormData('aspect_ratio', e.target.value)}
                      >
                        {ASPECT_RATIOS.map(ratio => (
                          <option key={ratio.value} value={ratio.value}>{ratio.label}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="control-group">
                    <label>스타일 프리셋</label>
                    <select 
                      value={formData.style_preset}
                      onChange={(e) => updateFormData('style_preset', e.target.value)}
                    >
                      {STYLE_PRESETS.map(style => (
                        <option key={style.value} value={style.value}>{style.label}</option>
                      ))}
                    </select>
                  </div>

                  <div className="control-group">
                    <label>시드 (0 = 랜덤)</label>
                    <input
                      type="number"
                      value={formData.seed}
                      onChange={(e) => updateFormData('seed', e.target.value)}
                      min="0"
                      max="2147483647"
                    />
                  </div>
                </div>

                {/* SD3.5 전용 설정 */}
                {generationType === 'sd35' && (
                  <div className="control-row">
                    <div className="control-group">
                      <label>SD3.5 모델</label>
                      <select 
                        value={formData.model}
                        onChange={(e) => updateFormData('model', e.target.value)}
                      >
                        {SD35_MODELS.map(model => (
                          <option key={model.value} value={model.value}>{model.label}</option>
                        ))}
                      </select>
                    </div>

                    {generationMode === 'image-to-image' && (
                      <div className="control-group">
                        <label>변형 강도</label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={formData.strength}
                          onChange={(e) => updateFormData('strength', parseFloat(e.target.value))}
                        />
                        <span>{formData.strength}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Ultra 전용 설정 */}
                {generationType === 'ultra' && (
                  <div className="control-row">
                    <div className="control-group">
                      <label>참조 이미지 (선택사항)</label>
                      <FileUpload onFileSelect={handleImageSelect} label="참조 이미지 업로드" />
                    </div>
                    {uploadedImage && (
                      <div className="control-group">
                        <label>참조 이미지 영향도</label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={formData.strength}
                          onChange={(e) => updateFormData('strength', parseFloat(e.target.value))}
                        />
                        <span>{formData.strength}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <button 
                className="generate-btn"
                onClick={generateImage}
                disabled={loading || !formData.prompt.trim()}
              >
                {loading ? '생성 중...' : '🎨 이미지 생성'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'control' && (
          <div className="control-panel">
            <div className="controls">
              <div className="control-group">
                <label>프롬프트</label>
                <textarea
                  value={formData.prompt}
                  onChange={(e) => updateFormData('prompt', e.target.value)}
                  placeholder="이미지 제어/편집 설명..."
                  rows={3}
                />
              </div>

              <div className="control-group">
                <label>입력 이미지</label>
                <FileUpload onFileSelect={handleImageSelect} />
                {uploadedImage && (
                  <div className="uploaded-image-preview">
                    <img 
                      src={URL.createObjectURL(uploadedImage)} 
                      alt="업로드된 이미지" 
                      style={{ maxWidth: '200px' }}
                    />
                  </div>
                )}
              </div>

              <div className="control-actions">
                <button 
                  onClick={() => controlImage('sketch')}
                  disabled={loading || !uploadedImage || !formData.prompt.trim()}
                >
                  ✏️ 스케치 → 이미지
                </button>
                <button 
                  onClick={() => controlImage('structure')}
                  disabled={loading || !uploadedImage || !formData.prompt.trim()}
                >
                  🏗️ 구조 제어
                </button>
                <button 
                  onClick={() => controlImage('style-guide')}
                  disabled={loading || !uploadedImage || !formData.prompt.trim()}
                >
                  🎨 스타일 가이드
                </button>
              </div>

              {/* 스타일 전송 */}
              <div className="style-transfer-section">
                <h3>스타일 전송</h3>
                <div className="control-group">
                  <label>스타일 이미지</label>
                  <FileUpload onFileSelect={handleStyleImageSelect} label="스타일 이미지 업로드" />
                  {styleImage && (
                    <div className="uploaded-image-preview">
                      <img 
                        src={URL.createObjectURL(styleImage)} 
                        alt="스타일 이미지" 
                        style={{ maxWidth: '200px' }}
                      />
                    </div>
                  )}
                </div>
                <button 
                  onClick={() => controlImage('style-transfer')}
                  disabled={loading || !uploadedImage || !styleImage}
                >
                  🔄 스타일 전송
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 결과 영역 */}
        <div className="result-area">
          {loading && <LoadingSpinner />}
          {error && <ErrorDisplay error={error} onClose={() => setError(null)} />}
          {generatedImage && (
            <div className="generated-image">
              <h3>생성된 이미지</h3>
              <img src={generatedImage} alt="생성된 이미지" />
              <div className="image-actions">
                <a 
                  href={generatedImage} 
                  download={`generated-image-${Date.now()}.${formData.output_format}`}
                  className="download-btn"
                >
                  💾 다운로드
                </a>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* CSS 스타일 */}
      <style jsx>{`
        .app-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        header {
          text-align: center;
          margin-bottom: 30px;
        }
        
        nav {
          display: flex;
          justify-content: center;
          gap: 10px;
          margin-top: 20px;
        }
        
        nav button {
          padding: 10px 20px;
          border: 2px solid #667eea;
          background: white;
          color: #667eea;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s;
        }
        
        nav button.active,
        nav button:hover {
          background: #667eea;
          color: white;
        }
        
        main {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
        }
        
        .controls {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
        }
        
        .control-group {
          margin-bottom: 20px;
        }
        
        .control-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: 600;
          color: #333;
        }
        
        .control-group input,
        .control-group select,
        .control-group textarea {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }
        
        .control-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }
        
        .file-upload {
          border: 2px dashed #ddd;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s;
        }
        
        .file-upload:hover,
        .file-upload.drag-over {
          border-color: #667eea;
          background: #f0f2ff;
        }
        
        .uploaded-image-preview {
          margin-top: 10px;
          text-align: center;
        }
        
        .uploaded-image-preview img {
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .generate-btn {
          width: 100%;
          padding: 15px;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }
        
        .generate-btn:hover:not(:disabled) {
          transform: translateY(-2px);
        }
        
        .generate-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .control-actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 10px;
          margin-bottom: 20px;
        }
        
        .control-actions button {
          padding: 10px;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        }
        
        .style-transfer-section {
          border-top: 1px solid #ddd;
          padding-top: 20px;
          margin-top: 20px;
        }
        
        .result-area {
          background: white;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
          text-align: center;
        }
        
        .loading-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error-display {
          background: #f8d7da;
          color: #721c24;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #f5c6cb;
        }
        
        .generated-image img {
          max-width: 100%;
          height: auto;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .download-btn {
          display: inline-block;
          margin-top: 15px;
          padding: 10px 20px;
          background: #28a745;
          color: white;
          text-decoration: none;
          border-radius: 5px;
          transition: background 0.3s;
        }
        
        .download-btn:hover {
          background: #218838;
        }
        
        @media (max-width: 768px) {
          main {
            grid-template-columns: 1fr;
          }
          
          .control-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ImageGenerationApp;