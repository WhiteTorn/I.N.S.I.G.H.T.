import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, ChevronLeft, ExternalLink, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import type { BriefingTopicsResponse, Topic, Post } from '../services/api';
import MarkdownRenderer from '../components/ui/MarkdownRenderer';

export default function TopicsBriefing() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [briefing, setBriefing] = useState<string | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [postsMap, setPostsMap] = useState<Record<string, Post>>({});
  const [unreferencedIds, setUnreferencedIds] = useState<string[]>([]);
  const [openTopic, setOpenTopic] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setBriefing(null);
    setTopics([]);
  setPostsMap({});
  setUnreferencedIds([]);
    try {
      const res: BriefingTopicsResponse = await apiService.generateBriefingWithTopics(selectedDate);
      if (res.success) {
        setBriefing(res.briefing || null);
        setTopics(res.topics || []);
    setPostsMap(res.posts || {});
    setUnreferencedIds(res.unreferenced_posts || []);
    // open first topic by default
    const first = (res.topics || [])[0];
    setOpenTopic(first ? first.id : null);
      } else {
        setError(res.error || 'Failed to generate topics');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Network error');
    } finally {
      setIsGenerating(false);
    }
  };

  const allPostsArray = useMemo(() => Object.entries(postsMap).sort((a, b) => Number(a[0]) - Number(b[0])), [postsMap]);

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4 transition-colors">
            <ChevronLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Topics Briefing</h1>
          <p className="text-sm text-gray-600">Group posts by AI-extracted topics</p>
        </div>
        <div className="space-y-3">
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              disabled={isGenerating}
              className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-lg bg-white text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors disabled:opacity-50"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGenerating ? (<><RefreshCw className="w-4 h-4 animate-spin" /> Generating...</>) : 'Generate'}
          </button>
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">{error}</div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {/* BRIEFING */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Briefing</h2>
            {briefing ? (
              <div className="prose max-w-none">
                <MarkdownRenderer content={briefing} />
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No briefing yet. Generate to see results.</div>
            )}
          </div>

          {/* spacer like a tab */}
          <div className="h-4" />

          {/* Numbered posts by topic with collapsible sections */}
          {topics.map((topic, tIndex) => {
            const isOpen = openTopic === topic.id;
            return (
              <div key={topic.id || `topic_${tIndex}`} className="bg-white border border-gray-200 rounded-lg mb-4 overflow-hidden">
                <button
                  onClick={() => setOpenTopic(isOpen ? null : topic.id)}
                  className="w-full text-left px-6 py-4 flex items-center justify-between hover:bg-gray-50"
                >
                  <span className="font-semibold text-gray-900">{tIndex + 1}. {topic.title || 'Untitled Topic'}</span>
                  <span className="text-xs text-gray-500">{isOpen ? 'Collapse' : 'Expand'}</span>
                </button>
                {isOpen && (
                  <div className="px-6 pb-6">
                    {topic.summary && (
                      <div className="text-sm text-gray-700 mb-4">
                        <MarkdownRenderer content={topic.summary} />
                      </div>
                    )}
                    <ol className="list-decimal pl-5 space-y-4">
                      {(topic.post_ids || []).map((pid, rIndex) => {
                        const post = postsMap[pid];
                        if (!post) return null;
                        const platformLabel = (post.platform || 'unknown').toUpperCase();
                        let dateLabel = 'Unknown date';
                        try { const d = new Date(post.date as string); if (!isNaN(d.getTime())) dateLabel = d.toLocaleDateString(); } catch {}
                        return (
                          <li key={`${pid}_${rIndex}`} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <h4 className="font-medium text-gray-900 mb-1">Post {pid}: {post.title || `${platformLabel} Post`}</h4>
                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                  <span>📡 {post.feed_title || post.source}</span>
                                  <span>📅 {dateLabel}</span>
                                  <span>🔗 {platformLabel}</span>
                                </div>
                              </div>
                              {post.url && (
                                <a href={post.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800">
                                  <ExternalLink className="w-4 h-4" />
                                </a>
                              )}
                            </div>
                            <div className="text-gray-700 text-sm leading-relaxed prose max-w-none">
                              <MarkdownRenderer content={post.content_html || post.content} />
                            </div>
                          </li>
                        );
                      })}
                    </ol>
                  </div>
                )}
              </div>
            );
          })}

          {/* Unreferenced posts shown separately, still with briefing above */}
          {unreferencedIds.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold mb-4">Unreferenced Posts</h3>
              <ol className="list-decimal pl-5 space-y-4">
                {unreferencedIds.map((pid) => {
                  const post = postsMap[pid];
                  if (!post) return null;
                  const platformLabel = (post.platform || 'unknown').toUpperCase();
                  let dateLabel = 'Unknown date';
                  try { const d = new Date(post.date as string); if (!isNaN(d.getTime())) dateLabel = d.toLocaleDateString(); } catch {}
                  return (
                    <li key={`unref_${pid}`} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-1">Post {pid}: {post.title || `${platformLabel} Post`}</h4>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>📡 {post.feed_title || post.source}</span>
                            <span>📅 {dateLabel}</span>
                            <span>🔗 {platformLabel}</span>
                          </div>
                        </div>
                        {post.url && (
                          <a href={post.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                      <div className="text-gray-700 text-sm leading-relaxed prose max-w-none">
                        <MarkdownRenderer content={post.content_html || post.content} />
                      </div>
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
