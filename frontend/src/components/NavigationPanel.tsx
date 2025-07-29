import { useState } from 'react';
import { ChevronRight, ChevronDown, Settings, Lightbulb, Calendar, Clock } from 'lucide-react';

interface NavigationPanelProps {
  className?: string;
}

export default function NavigationPanel({ className = "" }: NavigationPanelProps) {
  const [intelligenceTypeExpanded, setIntelligenceTypeExpanded] = useState(true);
  const [selectedIntelligenceType, setSelectedIntelligenceType] = useState('Daily Briefing');

  const intelligenceTypes = [
    'Daily Briefing',
    'Market Analysis', 
    'Security Updates',
    'Technology Trends',
    'Geopolitical Events'
  ];

  const sources = [
    { name: 'News', emoji: '📰', count: 42 },
    { name: 'Reddit', emoji: '🤖', count: 18 },
    { name: 'YouTube', emoji: '🎥', count: 7 },
    { name: 'Twitter/X', emoji: '🐦', count: 23 },
    { name: 'Blogs', emoji: '📝', count: 12 }
  ];

  const currentDate = new Date();
  const formattedDate = currentDate.toLocaleDateString('en-US', { 
    month: '2-digit', 
    day: '2-digit', 
    year: '2-digit' 
  });
  const formattedTime = currentDate.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZoneName: 'short'
  });

  return (
    <div className={`w-60 bg-gray-50 border-r border-gray-200 p-6 h-full flex flex-col ${className}`}>
      {/* Header Section */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">INSIGHT</h1>
        <p className="text-sm text-gray-600">Intelligence Platform</p>
      </div>

      {/* Learning Roadmap Button */}
      <div className="mb-6">
        <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-100 text-indigo-800 rounded-lg border border-indigo-200 hover:bg-indigo-150 transition-colors duration-200">
          <Lightbulb className="w-4 h-4" />
          <span className="font-medium">Learning Roadmap</span>
        </button>
      </div>

      {/* Intelligence Type Section */}
      <div className="mb-6">
        <button
          onClick={() => setIntelligenceTypeExpanded(!intelligenceTypeExpanded)}
          className="w-full flex items-center justify-between mb-3 text-sm font-semibold text-gray-900"
        >
          <span>Intelligence Type</span>
          {intelligenceTypeExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
        </button>
        
        {intelligenceTypeExpanded && (
          <div className="space-y-1">
            {intelligenceTypes.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedIntelligenceType(type)}
                className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors duration-200 ${
                  selectedIntelligenceType === type
                    ? 'nav-item active'
                    : 'nav-item text-gray-700 hover:bg-gray-100'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Date Range Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Date Range</h3>
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="font-mono text-sm text-gray-900">{formattedDate}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="font-mono text-xs text-gray-600">{formattedTime}</span>
          </div>
        </div>
      </div>

      {/* Sources Section */}
      <div className="mb-8 flex-1">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Sources</h3>
        <div className="space-y-2">
          {sources.map((source) => (
            <button
              key={source.name}
              className="w-full flex items-center justify-between px-3 py-2 bg-white border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all duration-200"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{source.emoji}</span>
                <span className="text-sm font-medium text-gray-900">{source.name}</span>
              </div>
              <span className="font-mono text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                {source.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Settings Footer */}
      <div className="border-t border-gray-200 pt-4">
        <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors duration-200">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
} 