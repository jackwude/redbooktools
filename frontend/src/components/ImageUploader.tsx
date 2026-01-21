import { useState, useCallback, DragEvent, ChangeEvent } from 'react';

interface ImageUploaderProps {
    /** 文件选择回调 */
    onFilesSelect: (files: File[]) => void;
    /** 是否禁用 */
    disabled?: boolean;
    /** 当前选中的文件列表 */
    selectedFiles?: File[];
    /** 清除/移除文件回调 */
    onRemoveFile?: (index: number) => void;
}

/**
 * 图片上传组件
 * 支持拖拽上传和点击选择（多文件）
 */
export function ImageUploader({
    onFilesSelect,
    disabled = false,
    selectedFiles = [],
    onRemoveFile,
}: ImageUploaderProps) {
    const [isDragOver, setIsDragOver] = useState(false);

    // 处理文件选择
    const handleFiles = useCallback(
        (files: FileList | File[]) => {
            const newFiles: File[] = [];
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];

            // 当前已有文件数量
            const currentCount = selectedFiles.length;
            let addedCount = 0;

            Array.from(files).forEach((file) => {
                // 检查总数限制
                if (currentCount + addedCount >= 20) {
                    return;
                }

                if (!validTypes.includes(file.type)) {
                    return; // 跳过不支持的格式
                }

                if (file.size > 10 * 1024 * 1024) {
                    return; // 跳过过大的文件
                }

                // 简单的排重（文件名+大小）
                const isDuplicate = selectedFiles.some(
                    existing => existing.name === file.name && existing.size === file.size
                );

                if (!isDuplicate) {
                    newFiles.push(file);
                    addedCount++;
                }
            });

            if (files.length > 0 && newFiles.length === 0 && currentCount >= 20) {
                alert('最多只能上传 20 张图片');
                return;
            }

            if (newFiles.length > 0) {
                onFilesSelect(newFiles);
            }
        },
        [onFilesSelect, selectedFiles]
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
                handleFiles(files);
            }
        },
        [disabled, handleFiles]
    );

    // 点击选择文件
    const handleInputChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                handleFiles(files);
            }
            // 重置 input 以允许重复选择相同文件
            e.target.value = '';
        },
        [handleFiles]
    );

    return (
        <div className="card">
            <h3 className="card-title">
                📤 上传小红书截图 ({selectedFiles.length}/20)
            </h3>

            {/* 上传区域 */}
            <div
                className={`upload-zone ${isDragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''
                    }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => {
                    if (!disabled && selectedFiles.length < 20) {
                        document.getElementById('file-input')?.click();
                    } else if (selectedFiles.length >= 20) {
                        alert('已达到最大上传数量限制');
                    }
                }}
                style={{ cursor: disabled || selectedFiles.length >= 20 ? 'not-allowed' : 'pointer' }}
            >
                <input
                    id="file-input"
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,image/webp"
                    onChange={handleInputChange}
                    style={{ display: 'none' }}
                    disabled={disabled || selectedFiles.length >= 20}
                    multiple // 支持多选
                />

                {selectedFiles.length > 0 ? (
                    <div className="upload-preview-grid">
                        {selectedFiles.map((file, index) => (
                            <div key={`${file.name}-${index}`} className="preview-item">
                                <img
                                    src={URL.createObjectURL(file)}
                                    alt={file.name}
                                    onLoad={(e) => URL.revokeObjectURL((e.target as HTMLImageElement).src)}
                                />
                                {!disabled && (
                                    <button
                                        className="preview-remove"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onRemoveFile?.(index);
                                        }}
                                        title="移除图片"
                                    >
                                        ✕
                                    </button>
                                )}
                            </div>
                        ))}
                        {selectedFiles.length < 20 && (
                            <div className="preview-add-more">
                                <span>+</span>
                            </div>
                        )}
                    </div>
                ) : (
                    <>
                        <div className="upload-zone-icon">📷</div>
                        <div className="upload-zone-title">
                            {isDragOver ? '松开鼠标添加图片' : '拖拽或点击上传截图'}
                        </div>
                        <div className="upload-zone-hint">
                            最多 20 张，支持 PNG、JPG、WebP
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default ImageUploader;
