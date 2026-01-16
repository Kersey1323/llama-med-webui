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
  const [isUploading, setIsUploading] = useState(false);
  const [showStartButton, setShowStartButton] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      console.log('文件已选择:', selectedFile.name);
      setFile(selectedFile);
      setError(null);
      setResult(null);
      setProgress(0);
      setShowStartButton(false);
      // 自动上传文件
      uploadFile(selectedFile);
    }
  };

  const uploadFile = async (fileToUpload) => {
    if (!fileToUpload) {
      setError('请选择文件');
      return;
    }

    setIsUploading(true);
    setProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', fileToUpload);

    try {
      const response = await axios.post('/api/batch/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });

      console.log('文件上传成功:', response.data);
      setShowStartButton(true);
      setProgress(0); // 重置进度条
    } catch (err) {
      console.error('文件上传失败:', err);
      setError(err.response?.data?.message || '上传文件时出错');
    } finally {
      setIsUploading(false);
    }
  };

  const handleStartProcessing = async () => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);
    setResult(null);
    setShowStartButton(false);

    try {
      // 开始处理
      const response = await axios.get('/api/batch/startProcess');
      const jobId = response.data.id;

      // 监控进度
      monitorProgress(jobId);
    } catch (err) {
      console.error('启动处理失败:', err);
      setError(err.response?.data?.message || '启动处理时出错');
      setIsProcessing(false);
    }
  };

  const monitorProgress = (jobId) => {
    const progressInterval = setInterval(async () => {
      try {
        const response = await axios.get('/api/batch/progress');
        const currentProgress = response.data.progress;
        setProgress(currentProgress);

        if (currentProgress >= 100) {
          clearInterval(progressInterval);
          handleProcessingComplete();
        }
      } catch (err) {
        console.error('获取进度失败:', err);
        clearInterval(progressInterval);
        setError('获取处理进度失败');
        setIsProcessing(false);
      }
    }, 2000); // 每2秒检查一次进度

    // 安全机制：最多检查5分钟
    setTimeout(() => {
      clearInterval(progressInterval);
      if (isProcessing) {
        setError('处理超时');
        setIsProcessing(false);
      }
    }, 300000);
  };

  const handleProcessingComplete = () => {
    setIsProcessing(false);
    setProgress(0);
    setResult({ message: '批量处理完成！请在历史记录中查看结果。' });

    // 重置文件相关状态
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      console.log('拖拽文件:', droppedFile.name);
      setFile(droppedFile);
      setError(null);
      setResult(null);
      setProgress(0);
      setShowStartButton(false);
      // 自动上传拖拽的文件
      uploadFile(droppedFile);
    }
  };

  const handleReset = () => {
    setFile(null);
    setProgress(0);
    setResult(null);
    setError(null);
    setIsProcessing(false);
    setIsUploading(false);
    setShowStartButton(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getProgressText = () => {
    if (isUploading) return '上传进度';
    if (isProcessing) return '处理进度';
    return '进度';
  };

  const showProgressBar = isUploading || isProcessing || progress > 0;

  return (
    <Layout>
      <div className="batch-process">
        <div className="batch-process-header">
          <h1>批量数据处理</h1>
          <p>上传 Excel 表格，AI 将自动识别并筛选出错误数据</p>
        </div>

        <div className="batch-process-content">
          <div
            className={`upload-area ${file ? 'has-file' : ''} ${isUploading ? 'uploading' : ''}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              type="file"
              onChange={handleFileChange}
              accept=".xlsx,.xls"
              ref={fileInputRef}
              className="file-input"
              disabled={isUploading || isProcessing}
            />
            <div className="upload-content">
              <i className="upload-icon">📁</i>
              <p>拖拽文件到这里或点击选择文件</p>
              <p className="upload-tip">支持 .xlsx, .xls 格式</p>
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
              <i className="error-icon">❌</i>
              {error}
            </div>
          )}

          {showStartButton && (
            <div className="start-button-container">
              <button
                className="start-process-button"
                onClick={handleStartProcessing}
                disabled={isProcessing}
              >
                <i className="start-icon">▶️</i>
                开始处理
              </button>
            </div>
          )}

          {showProgressBar && (
            <div className="progress-container">
              <p className="progress-label">{getProgressText()}</p>
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
                <i className="success-icon">✅</i>
                <p>{result.message}</p>
              </div>
            </div>
          )}

          <div className="button-group">
            <button
              className="reset-button"
              onClick={handleReset}
              disabled={isUploading || isProcessing}
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