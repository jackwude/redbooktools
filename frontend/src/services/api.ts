/**
 * API 服务类型定义
 */

/** 情感类型 */
export type SentimentType = 'positive' | 'negative' | 'neutral';

/** 帖子信息 */
export interface PostInfo {
    title: string;
    content: string;
    author: string;
    likes: number | null;
    comments: number | null;
    sentiment: SentimentType;
    sentiment_score: number;
    keywords: string[];
}

/** 情感分布 */
export interface SentimentDistribution {
    positive_count: number;
    negative_count: number;
    neutral_count: number;
    positive_ratio: number;
    negative_ratio: number;
    neutral_ratio: number;
}

/** 关键词信息 */
export interface KeywordInfo {
    word: string;
    count: number;
    sentiment: SentimentType;
}

/** 风险预警 */
export interface RiskAlert {
    level: 'high' | 'medium' | 'low';
    description: string;
    related_posts: string[];
}

/** 分析报告 */
export interface AnalysisReport {
    analysis_id: string;
    search_keyword: string | null;
    total_posts: number;
    sentiment_distribution: SentimentDistribution;
    top_keywords: KeywordInfo[];
    posts: PostInfo[];
    risk_alerts: RiskAlert[];
    summary: string;
    insights: string[];
    recommendations: string[];
    created_at: string;
}

/** API 响应 */
export interface AnalyzeResponse {
    success: boolean;
    message: string;
    data: AnalysisReport | null;
}

/** 分析状态 */
export type AnalysisStatus = 'idle' | 'uploading' | 'analyzing' | 'complete' | 'error';

/**
 * 上传图片并进行舆情分析
 * @param files 图片文件列表
 * @param searchKeyword 搜索关键词（可选）
 * @returns 分析结果
 */
export async function analyzeImage(
    files: File[],
    searchKeyword?: string
): Promise<AnalyzeResponse> {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('images', file);
    });

    if (searchKeyword) {
        formData.append('search_keyword', searchKeyword);
    }

    const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        let errorMessage = '分析请求失败';
        try {
            const error = await response.json();
            if (typeof error.detail === 'string') {
                errorMessage = error.detail;
            } else if (typeof error.message === 'string') {
                errorMessage = error.message;
            } else if (Array.isArray(error.detail)) {
                // 处理 FastAPI/Pydantic 的验证错误数组
                errorMessage = error.detail.map((e: any) => e.msg).join('; ');
            } else if (typeof error === 'object') {
                errorMessage = JSON.stringify(error);
            }
        } catch (e) {
            errorMessage = `请求失败 (${response.status} ${response.statusText})`;
        }
        throw new Error(errorMessage);
    }

    return response.json();
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch('/api/health');
        return response.ok;
    } catch {
        return false;
    }
}
