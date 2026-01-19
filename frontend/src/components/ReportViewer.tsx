import { useMemo } from 'react';
import {
    AnalysisReport,
    SentimentType,
    KeywordInfo,
    RiskAlert,
    PostInfo,
} from '../services/api';

interface ReportViewerProps {
    /** 分析报告数据 */
    report: AnalysisReport;
}

/**
 * 舆情报告展示组件
 * 展示完整的分析结果，包括情感分布、关键词、风险预警等
 */
export function ReportViewer({ report }: ReportViewerProps) {
    // 计算情感分布百分比用于饼图展示
    const sentimentData = useMemo(() => {
        const { sentiment_distribution } = report;
        return [
            {
                name: '正面',
                value: sentiment_distribution.positive_count,
                ratio: sentiment_distribution.positive_ratio,
                color: '#22C55E',
            },
            {
                name: '中性',
                value: sentiment_distribution.neutral_count,
                ratio: sentiment_distribution.neutral_ratio,
                color: '#3B82F6',
            },
            {
                name: '负面',
                value: sentiment_distribution.negative_count,
                ratio: sentiment_distribution.negative_ratio,
                color: '#EF4444',
            },
        ];
    }, [report.sentiment_distribution]);

    // 格式化日期
    const formattedDate = useMemo(() => {
        const date = new Date(report.created_at);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    }, [report.created_at]);

    return (
        <div className="report-section fade-in">
            {/* 报告头部 */}
            <div className="card summary-card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                            📊 舆情分析报告
                        </h2>
                        {report.search_keyword && (
                            <p style={{ color: 'var(--color-text-secondary)' }}>
                                关键词：<strong>{report.search_keyword}</strong>
                            </p>
                        )}
                    </div>
                    <div style={{ textAlign: 'right', color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
                        <div>报告 ID: {report.analysis_id}</div>
                        <div>{formattedDate}</div>
                    </div>
                </div>
                <p className="summary-text">{report.summary}</p>
            </div>

            {/* 统计概览 */}
            <div className="report-grid">
                <div className="card stat-card">
                    <div className="stat-value">{report.total_posts}</div>
                    <div className="stat-label">识别帖子数</div>
                </div>
                <div className="card stat-card">
                    <div className="stat-value positive">
                        {(report.sentiment_distribution.positive_ratio * 100).toFixed(1)}%
                    </div>
                    <div className="stat-label">正面情感占比</div>
                </div>
                <div className="card stat-card">
                    <div className="stat-value negative">
                        {(report.sentiment_distribution.negative_ratio * 100).toFixed(1)}%
                    </div>
                    <div className="stat-label">负面情感占比</div>
                </div>
                <div className="card stat-card">
                    <div className="stat-value neutral">
                        {(report.sentiment_distribution.neutral_ratio * 100).toFixed(1)}%
                    </div>
                    <div className="stat-label">中性情感占比</div>
                </div>
            </div>

            {/* 情感分布图 */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
                <h3 className="card-title">📈 情感分布</h3>
                <div className="chart-container">
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', gap: '3rem' }}>
                        {/* 简易饼图展示 */}
                        <div style={{ position: 'relative', width: '200px', height: '200px' }}>
                            <svg viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                                {sentimentData.reduce((acc, item, index) => {
                                    const prevOffset = acc.offset;
                                    const dashArray = item.ratio * 100;
                                    acc.elements.push(
                                        <circle
                                            key={item.name}
                                            cx="50"
                                            cy="50"
                                            r="40"
                                            fill="none"
                                            stroke={item.color}
                                            strokeWidth="20"
                                            strokeDasharray={`${dashArray} ${100 - dashArray}`}
                                            strokeDashoffset={-prevOffset}
                                            style={{ transition: 'all 0.5s ease' }}
                                        />
                                    );
                                    acc.offset += dashArray;
                                    return acc;
                                }, { elements: [] as JSX.Element[], offset: 0 }).elements}
                            </svg>
                            <div style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                transform: 'translate(-50%, -50%)',
                                textAlign: 'center',
                            }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{report.total_posts}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>帖子</div>
                            </div>
                        </div>
                        {/* 图例 */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {sentimentData.map((item) => (
                                <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{
                                        width: '16px',
                                        height: '16px',
                                        borderRadius: '4px',
                                        background: item.color,
                                    }} />
                                    <span>{item.name}</span>
                                    <span style={{ color: 'var(--color-text-muted)', marginLeft: 'auto' }}>
                                        {item.value} ({(item.ratio * 100).toFixed(1)}%)
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* 热门关键词 */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
                <h3 className="card-title">🔥 热门关键词</h3>
                <KeywordList keywords={report.top_keywords} />
            </div>

            {/* 风险预警 */}
            {report.risk_alerts.length > 0 && (
                <div className="card" style={{ marginBottom: '1.5rem' }}>
                    <h3 className="card-title">⚠️ 风险预警</h3>
                    <AlertList alerts={report.risk_alerts} />
                </div>
            )}

            {/* 关键洞察 */}
            <div className="report-grid">
                <div className="card">
                    <h3 className="card-title">💡 关键洞察</h3>
                    <div className="insight-list">
                        {report.insights.map((insight, index) => (
                            <div key={index} className="insight-item">
                                <div className="insight-icon">💡</div>
                                <span>{insight}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="card">
                    <h3 className="card-title">✅ 建议措施</h3>
                    <div className="recommendation-list">
                        {report.recommendations.map((rec, index) => (
                            <div key={index} className="recommendation-item">
                                <div className="recommendation-icon">✓</div>
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* 帖子详情列表 */}
            <div className="card" style={{ marginTop: '1.5rem' }}>
                <h3 className="card-title">📝 帖子详情</h3>
                <PostList posts={report.posts} />
            </div>
        </div>
    );
}

/** 关键词列表子组件 */
function KeywordList({ keywords }: { keywords: KeywordInfo[] }) {
    if (keywords.length === 0) {
        return <p style={{ color: 'var(--color-text-muted)' }}>暂无关键词数据</p>;
    }

    return (
        <div className="keyword-list">
            {keywords.map((kw, index) => (
                <span
                    key={index}
                    className={`keyword-tag ${kw.sentiment}`}
                >
                    {kw.word}
                    <span className="keyword-count">{kw.count}</span>
                </span>
            ))}
        </div>
    );
}

/** 风险预警列表子组件 */
function AlertList({ alerts }: { alerts: RiskAlert[] }) {
    const getAlertIcon = (level: string) => {
        switch (level) {
            case 'high':
                return '🔴';
            case 'medium':
                return '🟡';
            case 'low':
                return '🔵';
            default:
                return '⚪';
        }
    };

    const getLevelText = (level: string) => {
        switch (level) {
            case 'high':
                return '高风险';
            case 'medium':
                return '中风险';
            case 'low':
                return '低风险';
            default:
                return '未知';
        }
    };

    return (
        <div className="alert-list">
            {alerts.map((alert, index) => (
                <div key={index} className={`alert-item ${alert.level}`}>
                    <span className="alert-icon">{getAlertIcon(alert.level)}</span>
                    <div className="alert-content">
                        <div className="alert-title">{getLevelText(alert.level)}</div>
                        <div className="alert-desc">{alert.description}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}

/** 帖子列表子组件 */
function PostList({ posts }: { posts: PostInfo[] }) {
    if (posts.length === 0) {
        return <p style={{ color: 'var(--color-text-muted)' }}>暂无帖子数据</p>;
    }

    const getSentimentText = (sentiment: SentimentType) => {
        switch (sentiment) {
            case 'positive':
                return '正面';
            case 'negative':
                return '负面';
            case 'neutral':
                return '中性';
        }
    };

    return (
        <div className="post-list">
            {posts.map((post, index) => (
                <div key={index} className="post-item">
                    <div className="post-header">
                        <div className="post-title">{post.title}</div>
                        <span className={`post-sentiment ${post.sentiment}`}>
                            {getSentimentText(post.sentiment)}
                        </span>
                    </div>
                    {post.content && (
                        <div className="post-content">{post.content}</div>
                    )}
                    <div className="post-meta">
                        {post.author && (
                            <span className="post-meta-item">👤 {post.author}</span>
                        )}
                        {post.likes !== null && (
                            <span className="post-meta-item">❤️ {post.likes}</span>
                        )}
                        {post.comments !== null && (
                            <span className="post-meta-item">💬 {post.comments}</span>
                        )}
                        {post.keywords.length > 0 && (
                            <span className="post-meta-item">
                                🏷️ {post.keywords.slice(0, 3).join(', ')}
                            </span>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ReportViewer;
