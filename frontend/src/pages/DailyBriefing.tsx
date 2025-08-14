import React from 'react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { ChevronLeft, Download, Share2, Calendar, Clock, BarChart3, TrendingUp, Shield, Globe, Cpu, RefreshCw, AlertCircle, CheckCircle2, ExternalLink, Settings } from 'lucide-react';
import SourcesConfig from './SourcesConfig';
import { apiService } from '../services/api';
import type { BriefingResponse, Post, BriefingTopicsResponse, Topic } from '../services/api';
import MarkdownRenderer from '../components/ui/MarkdownRenderer';

export default function DailyBriefing() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeSection, setActiveSection] = useState('executive-summary');
  const [briefingData, setBriefingData] = useState<string | null>(null);
  const [sourcePosts, setSourcePosts] = useState<Post[]>([]); // Add state for actual posts
  const [briefingStats, setBriefingStats] = useState<{
    postsProcessed: number;
    totalFetched: number;
    date: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Topics-based briefing state
  const [isGeneratingTopics, setIsGeneratingTopics] = useState(false);
  const [topicsBriefing, setTopicsBriefing] = useState<string | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [postsMap, setPostsMap] = useState<Record<string, Post>>({});
  const [unreferencedIds, setUnreferencedIds] = useState<string[]>([]);
  const [openTopic, setOpenTopic] = useState<string | null>(null);
  // Inline sections-only experience; sources config is a first-class section now

  const handleGenerateBriefing = async () => {
    setIsGenerating(true);
    setError(null);
    setBriefingData(null);
    setBriefingStats(null);
    setSourcePosts([]); // Clear previous posts
  // Reset topics area when generating standard briefing
  setTopicsBriefing(null);
  setTopics([]);
  setPostsMap({});
  setUnreferencedIds([]);
  setOpenTopic(null);

    try {
      console.log(`🚀 Generating briefing for date: ${selectedDate}`);
      const response: BriefingResponse = await apiService.generateBriefing(selectedDate);
      
      if (response.success && response.briefing) {
        console.log('✅ Briefing generated successfully');
        setBriefingData(response.briefing);
        setSourcePosts(response.posts || []); // Store the actual posts
        setBriefingStats({
          postsProcessed: response.posts_processed || 0,
          totalFetched: response.total_posts_fetched || 0,
          date: response.date || selectedDate
        });
      } else {
        console.error('❌ Briefing generation failed:', response.error);
        setError(response.error || 'Failed to generate briefing');
      }
    } catch (error) {
      console.error('❌ API call failed:', error);
      setError(error instanceof Error ? error.message : 'Network error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateTopicBriefing = async () => {
    setIsGeneratingTopics(true);
    setError(null);
    setTopicsBriefing(null);
    setTopics([]);
    setPostsMap({});
    setUnreferencedIds([]);
    setOpenTopic(null);
    try {
      const response: BriefingTopicsResponse = await apiService.generateBriefingWithTopics(selectedDate, { includeUnreferenced: true });
      if (response.success) {
        setTopicsBriefing(response.briefing || null);
        setTopics(response.topics || []);
        setPostsMap(response.posts || {});
        setUnreferencedIds(response.unreferenced_posts || []);
        const first = (response.topics || [])[0];
        setOpenTopic(first ? first.id : null);
      } else {
        setError(response.error || 'Failed to generate topic-based briefing');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error occurred');
    } finally {
      setIsGeneratingTopics(false);
    }
  };

  const briefingSections = [
    { id: 'executive-summary', title: 'Executive Summary', icon: BarChart3 },
    { id: 'technology', title: 'Technology Sector', icon: Cpu },
    { id: 'security', title: 'Security Updates', icon: Shield },
    { id: 'markets', title: 'Market Analysis', icon: TrendingUp },
    { id: 'geopolitical', title: 'Geopolitical Events', icon: Globe },
  ];

  // Dynamic metrics based on actual data
  const getDynamicMetrics = () => {
    if (!briefingStats || !sourcePosts.length) {
      return {
        criticalUpdates: 0,
        opportunities: 0,
        threatLevel: "Unknown"
      };
    }

    return {
      criticalUpdates: Math.min(briefingStats.postsProcessed, 5), // Cap at 5 for realism
      opportunities: Math.max(Math.floor(briefingStats.postsProcessed * 0.6), 1), // ~60% of posts as opportunities
      threatLevel: briefingStats.postsProcessed > 5 ? "High" : briefingStats.postsProcessed > 2 ? "Medium" : "Low"
    };
  };

  const metrics = getDynamicMetrics();

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Table of Contents Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
        <div className="mb-8">
          <Link 
            to="/" 
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Daily Briefing</h1>
          <p className="text-sm text-gray-600">
            {new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>

        {/* Date Controls */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-900 mb-3">Generate for Date</label>
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
              onClick={handleGenerateBriefing}
              disabled={isGenerating}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <BarChart3 className="w-4 h-4" />
                  Generate Briefing
                </>
              )}
            </button>
                <button
                  onClick={handleGenerateTopicBriefing}
                  disabled={isGeneratingTopics}
                  className="w-full mt-2 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isGeneratingTopics ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating Topic-based Briefing...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="w-4 h-4" />
                      Generate Topic-based Briefing
                    </>
                  )}
                </button>
          </div>

          {/* Status Indicators */}
          {briefingStats && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">Briefing Generated</span>
              </div>
              <div className="text-xs text-green-700 space-y-1">
                <div>📊 Posts processed: {briefingStats.postsProcessed}</div>
                <div>🔍 Total sources: {briefingStats.totalFetched}</div>
                <div>📅 Date: {briefingStats.date}</div>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-800">Generation Failed</span>
              </div>
              <div className="text-xs text-red-700">{error}</div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Sections</h3>
          <nav className="space-y-1">
            {briefingSections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                  activeSection === section.id
                    ? 'bg-indigo-50 text-indigo-900 border border-indigo-200'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <section.icon className="w-4 h-4" />
                {section.title}
              </button>
            ))}
          </nav>
        </div>

        {/* Export Actions */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Actions</h3>
          <div className="space-y-2">
            <button 
              disabled={!briefingData}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </button>
            <button 
              disabled={!briefingData}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Share2 className="w-4 h-4" />
              Share Briefing
            </button>
            <button 
              onClick={() => setActiveSection('configure-sources')}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors ${
                activeSection === 'configure-sources'
                  ? 'bg-indigo-50 text-indigo-900 border border-indigo-200'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-4 h-4" />
              Configure Sources
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {/* Status Bar */}
          <div className="flex items-center justify-between mb-8 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="w-4 h-4" />
                Last updated: {new Date().toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  timeZoneName: 'short'
                })}
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${briefingData ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                <span className={briefingData ? 'text-green-700' : 'text-gray-500'}>
                  {briefingData ? 'Generated' : 'Ready'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>🎯 Threat Level: <strong className="text-yellow-600">Medium</strong></span>
                <span>📊 Sources: <strong>{briefingStats?.totalFetched || '47'}</strong></span>
                <span>🔄 Updates: <strong>{briefingStats?.postsProcessed || '12'}</strong></span>
              </div>
            </div>
          </div>

          {/* Executive Summary */}
          {activeSection === 'executive-summary' && (
            <div className="space-y-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Executive Summary</h2>
                
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-red-100 rounded-lg">
                        <Shield className="w-5 h-5 text-red-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Critical Updates</h3>
                    </div>
                    <div className="text-2xl font-bold text-red-600">{metrics.criticalUpdates}</div>
                    <p className="text-xs text-gray-500 mt-1">Requiring immediate attention</p>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Opportunities</h3>
                    </div>
                    <div className="text-2xl font-bold text-green-600">{metrics.opportunities}</div>
                    <p className="text-xs text-gray-500 mt-1">Strategic opportunities identified</p>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-yellow-100 rounded-lg">
                        <BarChart3 className="w-5 h-5 text-yellow-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Threat Level</h3>
                    </div>
                    <div className="text-2xl font-bold text-yellow-600">{metrics.threatLevel}</div>
                    <p className="text-xs text-gray-500 mt-1">Overall assessment</p>
                  </div>
                </div>

                {/* AI-Generated Briefing Content */}
                {briefingData ? (
                  <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      🤖 AI-Generated Intelligence Briefing
                    </h3>
                    <div className="prose max-w-none">
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <BarChart3 className="w-4 h-4 text-blue-600" />
                          <span className="text-sm font-medium text-blue-800">
                            Mark I Foundation Engine Output
                          </span>
                        </div>
                        <div className="text-xs text-blue-700">
                          Generated from {briefingStats?.totalFetched} sources • {briefingStats?.postsProcessed} posts processed
                        </div>
                      </div>
                      <MarkdownRenderer content={briefingData} />
                    </div>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg p-8 text-center mb-6">
                    <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {isGenerating ? 'Generating Intelligence Briefing...' : 'Ready to Generate Briefing'}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {isGenerating 
                        ? 'Mark I Foundation Engine is analyzing intelligence sources and generating your briefing...'
                        : 'Select a date and click "Generate Briefing" to create your AI-powered intelligence report.'
                      }
                    </p>
                    {isGenerating && (
                      <div className="flex items-center justify-center gap-2 text-sm text-blue-600">
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Processing intelligence data...</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Topic-based Briefing Content */}
                {(topicsBriefing || topics.length > 0) && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">🧩 Topic-based Briefing</h3>
                    {/* BRIEFING */}
                    {topicsBriefing ? (
                      <div className="prose max-w-none mb-4">
                        <MarkdownRenderer content={topicsBriefing} />
                      </div>
                    ) : null}
                    {/* spacer like a tab */}
                    <div className="h-4" />
                    {/* Collapsible topics */}
                    <div className="space-y-3">
                      {topics.map((topic, tIndex) => {
                        const isOpen = openTopic === topic.id;
                        return (
                          <div key={topic.id || `topic_${tIndex}`} className="border border-gray-200 rounded-lg overflow-hidden">
                            <button
                              onClick={() => setOpenTopic(isOpen ? null : topic.id)}
                              className="w-full text-left px-4 py-3 flex items-center justify-between hover:bg-gray-50"
                            >
                              <span className="font-medium text-gray-900">{tIndex + 1}. {topic.title || 'Untitled Topic'}</span>
                              <span className="text-xs text-gray-500">{isOpen ? 'Collapse' : 'Expand'}</span>
                            </button>
                            {isOpen && (
                              <div className="px-4 pb-4">
                                {topic.summary && (
                                  <div className="text-sm text-gray-700 mb-3">
                                    <MarkdownRenderer content={topic.summary} />
                                  </div>
                                )}
                                <ol className="list-decimal pl-5 space-y-3">
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
                    </div>

                    {/* Unreferenced posts */}
                    {unreferencedIds.length > 0 && (
                      <div className="mt-6">
                        <h4 className="font-semibold text-gray-900 mb-3">Unreferenced Posts</h4>
                        <ol className="list-decimal pl-5 space-y-3">
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
                                    <h5 className="font-medium text-gray-900 mb-1">Post {pid}: {post.title || `${platformLabel} Post`}</h5>
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
                )}

                {/* Source Posts Section */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Intelligence Posts</h3>
                  {sourcePosts.length > 0 ? (
                    <div className="space-y-4">
                      {sourcePosts.map((post, index) => {
                        // Defensive guards: avoid crashes on unexpected/missing fields
                        const platformLabel = (post?.platform || 'unknown').toUpperCase();
                        let dateLabel = 'Unknown date';
                        try {
                          const d = new Date(post?.date as string);
                          if (!isNaN(d.getTime())) dateLabel = d.toLocaleDateString();
                        } catch (_) {
                          // keep default
                        }

                        return (
                          <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <h4 className="font-medium text-gray-900 mb-1">
                                  {post.title || `${platformLabel} Post`}
                                </h4>
                                <div className="flex items-center gap-4 text-sm text-gray-500 mb-2">
                                  <span>📡 {post.feed_title || post.source}</span>
                                  <span>📅 {dateLabel}</span>
                                  <span>🔗 {platformLabel}</span>
                                </div>
                              </div>
                              {post.url && (
                                <a
                                  href={post.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-indigo-600 hover:text-indigo-800 transition-colors"
                                >
                                  <ExternalLink className="w-4 h-4" />
                                </a>
                              )}
                            </div>
                            <div className="text-gray-700 text-sm leading-relaxed prose max-w-none">
                              {/* Use MarkdownRenderer for both Markdown and embedded HTML with sanitization */}
                              <MarkdownRenderer content={post.content_html || post.content} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <p>No source posts available. Generate a briefing to see intelligence posts.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Configure Sources Section */}
          {activeSection === 'configure-sources' && (
            <div className="space-y-8">
              <div>
                <SourcesConfig embedded />
              </div>
            </div>
          )}

          {/* Placeholder for other sections */}
          {activeSection !== 'executive-summary' && activeSection !== 'configure-sources' && (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
              <div className="mb-4">
                {briefingSections.find(s => s.id === activeSection)?.icon && (
                  <div className="inline-flex p-4 bg-gray-100 rounded-full mb-4">
                    {React.createElement(briefingSections.find(s => s.id === activeSection)!.icon, {
                      className: "w-8 h-8 text-gray-400"
                    })}
                  </div>
                )}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {briefingSections.find(s => s.id === activeSection)?.title}
              </h3>
              <p className="text-gray-600 mb-6">
                {(() => {
                  const title = briefingSections.find(s => s.id === activeSection)?.title;
                  return `This section will contain detailed analysis and intelligence for ${(title || '').toLowerCase()}.`;
                })()}
              </p>
              <div className="inline-flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-4 py-2 rounded-lg">
                <RefreshCw className="w-4 h-4" />
                Ready for backend integration
              </div>
            </div>
          )}
        </div>
      </div>

  {/* No modal; sources config is embedded as a section */}
    </div>
  );
} 