import { useState } from 'react';
import { Play, Clock, ExternalLink, Plus, Zap, BookOpen, Share2, Heart } from 'lucide-react';

interface IntelligenceCardProps {
  title: string;
  summary: string;
  originalContent: string;
  timestamp: string;
  source: string;
  type?: 'article' | 'video' | 'reddit' | 'tweet';
  videoData?: {
    duration: string;
    channel: string;
    thumbnail?: string;
  };
  url?: string;
  className?: string;
}

export default function IntelligenceCard({
  title,
  summary,
  originalContent,
  timestamp,
  source,
  type = 'article',
  videoData,
  url,
  className = ""
}: IntelligenceCardProps) {
  const [showOriginalContent, setShowOriginalContent] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: '2-digit', 
      day: '2-digit' 
    }) + ' ' + date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  const getSourceEmoji = (source: string) => {
    switch (source.toLowerCase()) {
      case 'youtube': return '🎥';
      case 'reddit': return '🤖';
      case 'twitter': 
      case 'x': return '🐦';
      case 'news': return '📰';
      default: return '📝';
    }
  };

  return (
    <article className={`intelligence-card ${className}`}>
      {/* Video Indicator */}
      {type === 'video' && videoData && (
        <div className="video-indicator">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Play className="w-4 h-4 icon" />
              <span className="text-sm font-medium">{videoData.channel}</span>
            </div>
            <div className="duration px-2 py-1 rounded text-xs font-mono">
              {videoData.duration}
            </div>
          </div>
        </div>
      )}

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 leading-tight">
        {title}
      </h3>

      {/* Timestamp and Source */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-mono text-gray-500">
          {formatTimestamp(timestamp)}
        </span>
        <span className="text-gray-300">•</span>
        <div className="flex items-center gap-1">
          <span className="text-sm">{getSourceEmoji(source)}</span>
          <span className="text-xs text-gray-600 font-medium">{source}</span>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-4">
        <p className="summary-text">{summary}</p>
      </div>

      {/* Collapsible Original Content */}
      <details className="mb-4">
        <summary 
          className="content-toggle cursor-pointer select-none"
          onClick={(e) => {
            e.preventDefault();
            setShowOriginalContent(!showOriginalContent);
          }}
        >
          {showOriginalContent ? '▼ Hide Original Content' : '▶ View Original Content'}
        </summary>
        {showOriginalContent && (
          <div className="mt-3 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
              {originalContent}
            </p>
            {url && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  View Original Source
                </a>
              </div>
            )}
          </div>
        )}
      </details>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        <button className="action-btn bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100">
          <Plus className="w-3 h-3" />
          Add to Roadmap
        </button>
        
        <button className="action-btn bg-yellow-50 text-yellow-700 border border-yellow-200 hover:bg-yellow-100">
          <Zap className="w-3 h-3" />
          Process
        </button>
        
        <button className="action-btn bg-green-50 text-green-700 border border-green-200 hover:bg-green-100">
          <BookOpen className="w-3 h-3" />
          Deep Dive
        </button>
        
        <button className="action-btn bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100">
          <Share2 className="w-3 h-3" />
          Share
        </button>
        
        <button className="action-btn bg-red-50 text-red-700 border border-red-200 hover:bg-red-100">
          <Heart className="w-3 h-3" />
          Save
        </button>
      </div>
    </article>
  );
} 