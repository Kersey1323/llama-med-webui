import React, { useState, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import './BatchProcess.css';

const BatchProcess = () => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('请选择文件');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/batch/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '处理文件时出错');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleReset = () => {
    setFile(null);
    setProgress(0);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Layout>
      <div className="batch-process">
        <div className="batch-process-header">
          <h1>批量数据处理</h1>
          <p>上传文件进行批量处理</p>
        </div>

        <div className="batch-process-content">
          <div 
            className={`upload-area ${file ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              type="file"
              onChange={handleFileChange}
              accept=".txt,.csv,.xlsx"
              ref={fileInputRef}
              className="file-input"
            />
            <div className="upload-content">
              <i className="upload-icon">📁</i>
              <p>拖拽文件到这里或点击选择文件</p>
              {file && (
                <div className="file-info">
                  <p>已选择: {file.name}</p>
                  <p>大小: {(file.size / 1024).toFixed(2)} KB</p>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {isProcessing && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="progress-text">{progress}%</p>
            </div>
          )}

          {result && (
            <div className="result-container">
              <h3>处理结果</h3>
              <div className="result-content">
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </div>
            </div>
          )}

          <div className="button-group">
            <button 
              className="submit-button"
              onClick={handleSubmit}
              disabled={!file || isProcessing}
            >
              {isProcessing ? '处理中...' : '开始处理'}
            </button>
            <button 
              className="reset-button"
              onClick={handleReset}
              disabled={!file && !result}
            >
              重置
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BatchProcess; 