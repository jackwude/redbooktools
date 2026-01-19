import { useState, useCallback } from 'react';
import { ImageUploader } from './components/ImageUploader';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ReportViewer } from './components/ReportViewer';
import {
    analyzeImage,
    AnalysisReport,
    AnalysisStatus,
} from './services/api';

/**
 * 小红书舆情分析工具 - 主应用组件
 */
function App() {
    // 状态管理
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [searchKeyword, setSearchKeyword] = useState('');
    const [status, setStatus] = useState<AnalysisStatus>('idle');
    const [errorMessage, setErrorMessage] = useState<string>('');
    const [report, setReport] = useState<AnalysisReport | null>(null);

    // 处理文件选择
    const handleFileSelect = useCallback((file: File) => {
        setSelectedFile(file);
        setReport(null);
        setStatus('idle');
        setErrorMessage('');
    }, []);

    // 清除文件
    const handleClearFile = useCallback(() => {
        setSelectedFile(null);
        setReport(null);
        setStatus('idle');
        setErrorMessage('');
    }, []);

    // 开始分析
    const handleAnalyze = useCallback(async () => {
        if (!selectedFile) {
            alert('请先上传截图');
            return;
        }

        try {
            setStatus('uploading');
            setErrorMessage('');
            setReport(null);

            // 模拟上传延迟
            await new Promise((resolve) => setTimeout(resolve, 500));
            setStatus('analyzing');

            // 调用分析 API
            const response = await analyzeImage(
                selectedFile,
                searchKeyword || undefined
            );

            if (response.success && response.data) {
                setReport(response.data);
                setStatus('complete');
            } else {
                throw new Error(response.message || '分析失败');
            }
        } catch (error) {
            console.error('分析失败:', error);
            setStatus('error');
            setErrorMessage(
                error instanceof Error ? error.message : '未知错误，请重试'
            );
        }
    }, [selectedFile, searchKeyword]);

    // 重新分析
    const handleReset = useCallback(() => {
        setSelectedFile(null);
        setSearchKeyword('');
        setStatus('idle');
        setErrorMessage('');
        setReport(null);
    }, []);

    const isProcessing = status === 'uploading' || status === 'analyzing';

    return (
        <div className="app-container">
            {/* 头部 */}
            <header className="app-header">
                <div className="app-logo">
                    <div className="app-logo-icon">📊</div>
                    <h1 className="app-title">小红书舆情分析工具</h1>
                </div>
                <p className="app-subtitle">
                    上传小红书截图，智能识别内容并生成专业舆情分析报告
                </p>
            </header>

            {/* 主内容区 */}
            <main>
                {/* 上传区域 */}
                <ImageUploader
                    onFileSelect={handleFileSelect}
                    disabled={isProcessing}
                    selectedFile={selectedFile}
                    onClear={handleClearFile}
                />

                {/* 搜索关键词输入（可选） */}
                <div className="card" style={{ marginTop: '1.5rem' }}>
                    <h3 className="card-title">🔍 搜索关键词（可选）</h3>
                    <input
                        type="text"
                        value={searchKeyword}
                        onChange={(e) => setSearchKeyword(e.target.value)}
                        placeholder="输入关键词可帮助优化分析结果..."
                        disabled={isProcessing}
                        style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            fontSize: '1rem',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-md)',
                            background: 'var(--color-bg-elevated)',
                            color: 'var(--color-text-primary)',
                            outline: 'none',
                            transition: 'border-color var(--transition-fast)',
                        }}
                        onFocus={(e) => {
                            e.target.style.borderColor = 'var(--color-primary)';
                        }}
                        onBlur={(e) => {
                            e.target.style.borderColor = 'var(--color-border)';
                        }}
                    />
                </div>

                {/* 分析按钮 */}
                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                    {status === 'complete' ? (
                        <button className="btn btn-secondary" onClick={handleReset}>
                            🔄 重新分析
                        </button>
                    ) : (
                        <button
                            className="btn btn-primary"
                            onClick={handleAnalyze}
                            disabled={!selectedFile || isProcessing}
                        >
                            {isProcessing ? (
                                <>
                                    <span className="progress-spinner" style={{ width: '16px', height: '16px' }} />
                                    分析中...
                                </>
                            ) : (
                                <>✨ 开始分析</>
                            )}
                        </button>
                    )}
                </div>

                {/* 进度指示器 */}
                <AnalysisProgress status={status} message={errorMessage} />

                {/* 错误提示 */}
                {status === 'error' && (
                    <div
                        className="card fade-in"
                        style={{
                            marginTop: '1.5rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderColor: 'rgba(239, 68, 68, 0.3)',
                        }}
                    >
                        <p style={{ color: 'var(--color-negative)', margin: 0 }}>
                            ❌ {errorMessage || '分析过程中发生错误，请重试'}
                        </p>
                    </div>
                )}

                {/* 分析报告 */}
                {report && <ReportViewer report={report} />}
            </main>

            {/* 页脚 */}
            <footer
                style={{
                    marginTop: '4rem',
                    paddingTop: '2rem',
                    borderTop: '1px solid var(--color-border)',
                    textAlign: 'center',
                    color: 'var(--color-text-muted)',
                    fontSize: '0.875rem',
                }}
            >
                <p>小红书舆情分析工具 © 2026 | 基于 AI 多模态能力驱动</p>
            </footer>
        </div>
    );
}

export default App;
