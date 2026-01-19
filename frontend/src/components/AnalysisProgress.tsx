import { AnalysisStatus } from '../services/api';

interface AnalysisProgressProps {
    /** 当前分析状态 */
    status: AnalysisStatus;
    /** 进度消息 */
    message?: string;
}

/**
 * 分析进度组件
 * 显示分析过程中的进度状态
 */
export function AnalysisProgress({ status, message }: AnalysisProgressProps) {
    // 根据状态计算进度百分比
    const getProgress = (): number => {
        switch (status) {
            case 'idle':
                return 0;
            case 'uploading':
                return 20;
            case 'analyzing':
                return 60;
            case 'complete':
                return 100;
            case 'error':
                return 0;
            default:
                return 0;
        }
    };

    // 根据状态获取提示文字
    const getStatusText = (): string => {
        switch (status) {
            case 'idle':
                return '等待上传...';
            case 'uploading':
                return '正在上传图片...';
            case 'analyzing':
                return '正在分析舆情数据...';
            case 'complete':
                return '分析完成！';
            case 'error':
                return message || '分析失败';
            default:
                return '';
        }
    };

    // 如果是空闲状态，不显示进度条
    if (status === 'idle') {
        return null;
    }

    const progress = getProgress();
    const isProcessing = status === 'uploading' || status === 'analyzing';

    return (
        <div className="progress-container fade-in">
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{ width: `${progress}%` }}
                />
            </div>
            <div className="progress-status">
                {isProcessing && <div className="progress-spinner" />}
                {status === 'complete' && <span>✅</span>}
                {status === 'error' && <span>❌</span>}
                <span>{getStatusText()}</span>
            </div>
        </div>
    );
}

export default AnalysisProgress;
