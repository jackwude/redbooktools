import { useState, useCallback, DragEvent, ChangeEvent } from 'react';

interface ImageUploaderProps {
    /** 文件选择回调 */
    onFileSelect: (file: File) => void;
    /** 是否禁用 */
    disabled?: boolean;
    /** 当前选中的文件 */
    selectedFile?: File | null;
    /** 清除文件回调 */
    onClear?: () => void;
}

/**
 * 图片上传组件
 * 支持拖拽上传和点击选择
 */
export function ImageUploader({
    onFileSelect,
    disabled = false,
    selectedFile,
    onClear,
}: ImageUploaderProps) {
    const [isDragOver, setIsDragOver] = useState(false);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    // 处理文件选择
    const handleFile = useCallback(
        (file: File) => {
            // 验证文件类型
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                alert('请上传 PNG、JPG 或 WebP 格式的图片');
                return;
            }

            // 验证文件大小（最大 10MB）
            if (file.size > 10 * 1024 * 1024) {
                alert('图片大小不能超过 10MB');
                return;
            }

            // 生成预览 URL
            const url = URL.createObjectURL(file);
            setPreviewUrl(url);

            onFileSelect(file);
        },
        [onFileSelect]
    );

    // 拖拽事件处理
    const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        if (!disabled) {
            setIsDragOver(true);
        }
    }, [disabled]);

    const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);

    const handleDrop = useCallback(
        (e: DragEvent<HTMLDivElement>) => {
            e.preventDefault();
            setIsDragOver(false);

            if (disabled) return;

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        },
        [disabled, handleFile]
    );

    // 点击选择文件
    const handleInputChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                handleFile(files[0]);
            }
        },
        [handleFile]
    );

    // 清除选中的文件
    const handleClear = useCallback(() => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
        setPreviewUrl(null);
        onClear?.();
    }, [previewUrl, onClear]);

    return (
        <div className="card">
            <h3 className="card-title">
                📤 上传小红书截图
            </h3>

            {/* 上传区域 */}
            <div
                className={`upload-zone ${isDragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''
                    }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => {
                    if (!disabled && !selectedFile) {
                        document.getElementById('file-input')?.click();
                    }
                }}
                style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}
            >
                {/* 隐藏的文件输入 */}
                <input
                    id="file-input"
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,image/webp"
                    onChange={handleInputChange}
                    style={{ display: 'none' }}
                    disabled={disabled}
                />

                {/* 预览或提示 */}
                {previewUrl && selectedFile ? (
                    <div className="upload-preview">
                        <img src={previewUrl} alt="预览" />
                        {!disabled && (
                            <button
                                className="upload-preview-remove"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleClear();
                                }}
                                title="移除图片"
                            >
                                ✕
                            </button>
                        )}
                        <p style={{ marginTop: '1rem', color: 'var(--color-text-secondary)' }}>
                            {selectedFile.name}
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="upload-zone-icon">📷</div>
                        <div className="upload-zone-title">
                            {isDragOver ? '松开鼠标上传图片' : '拖拽或点击上传截图'}
                        </div>
                        <div className="upload-zone-hint">
                            支持 PNG、JPG、WebP 格式，最大 10MB
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default ImageUploader;
