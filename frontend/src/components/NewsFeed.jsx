/**
 * NewsFeed Component
 * 
 * Scrollable list of news items with sentiment badges
 */

function NewsFeed({ news }) {
    // Get badge color based on sentiment
    const getBadgeColor = (sentiment) => {
        if (sentiment >= 0.5) return '#22c55e';
        if (sentiment >= 0.3) return '#84cc16';
        if (sentiment <= -0.3) return '#ef4444';
        return '#f59e0b';
    };

    // Format relative time
    const formatTime = (dateStr) => {
        if (!dateStr) return '';

        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffWeeks = Math.floor(diffDays / 7);

        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays < 7) return `${diffDays} days ago`;
        return `${diffWeeks} weeks ago`;
    };

    return (
        <div className="glass-card p-4 h-full flex flex-col">
            <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                Latest News
            </h3>

            {!news || news.length === 0 ? (
                <div className="flex-1 flex items-center justify-center">
                    <p style={{ color: 'var(--text-secondary)' }}>No news available.</p>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                    {news.map((item, index) => (
                        <div
                            key={index}
                            className="news-item p-3 rounded-lg cursor-pointer"
                            style={{ background: 'rgba(30, 30, 60, 0.5)' }}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div className="flex-1 min-w-0">
                                    <p
                                        className="text-sm font-medium leading-snug mb-1 line-clamp-2"
                                        style={{ color: 'var(--text-primary)' }}
                                    >
                                        {item.link ? (
                                            <a
                                                href={item.link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="hover:underline"
                                            >
                                                {item.title}
                                            </a>
                                        ) : (
                                            item.title
                                        )}
                                    </p>
                                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                                        {formatTime(item.published)}
                                    </p>
                                </div>

                                {/* Sentiment badge */}
                                <div
                                    className="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold text-white"
                                    style={{ backgroundColor: getBadgeColor(item.sentiment) }}
                                >
                                    {item.sentiment?.toFixed(2) || '0.00'}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default NewsFeed;
