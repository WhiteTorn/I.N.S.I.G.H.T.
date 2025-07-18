import { Calendar, Settings, Filter, ChevronDown, ChevronRight, Map } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ManualContentEntry } from '@/components/ManualContentEntry';

interface NavigationPanelProps {
  selectedDate: Date;
  onDateChange: (date: Date) => void;
  selectedSources: string[];
  onSourcesChange: (sources: string[]) => void;
  onManualContentAdded?: (content: any) => void;
}

const sources = [
  { id: 'all', name: 'All Sources', icon: '🌐', count: 142 },
  { id: 'telegram', name: 'Telegram', icon: '📱', count: 45 },
  { id: 'twitter', name: 'Twitter/X', icon: '🐦', count: 38 },
  { id: 'reddit', name: 'Reddit', icon: '📖', count: 29 },
  { id: 'news', name: 'News Outlets', icon: '📰', count: 30 },
];

const briefingTypes = [
  { id: 'daily', name: 'Daily Briefing', icon: '📅', active: true },
  { id: 'weekly', name: 'Weekly Summary', icon: '📊', active: false },
  { id: 'monthly', name: 'Monthly Report', icon: '📈', active: false },
  { id: 'yearly', name: 'Annual Review', icon: '📋', active: false },
];

export const NavigationPanel = ({ 
  selectedDate, 
  onDateChange, 
  selectedSources, 
  onSourcesChange,
  onManualContentAdded 
}: NavigationPanelProps) => {
  const [selectedBriefing, setSelectedBriefing] = useState('daily');
  const [briefingSectionExpanded, setBriefingSectionExpanded] = useState(true);
  const navigate = useNavigate();

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const toggleSource = (sourceId: string) => {
    if (sourceId === 'all') {
      onSourcesChange(['all']);
    } else {
      const newSources = selectedSources.includes(sourceId)
        ? selectedSources.filter(s => s !== sourceId)
        : [...selectedSources.filter(s => s !== 'all'), sourceId];
      
      onSourcesChange(newSources.length === 0 ? ['all'] : newSources);
    }
  };

  const getDateRangeText = (type: string) => {
    const date = selectedDate;
    switch (type) {
      case 'weekly':
        return `Week of ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
      case 'monthly':
        return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      case 'yearly':
        return date.getFullYear().toString();
      default:
        return formatDate(date);
    }
  };

  return (
    <div className="w-60 bg-gray-50 border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">INSIGHT</h1>
        <p className="text-sm text-gray-500 mt-1">Intelligence Platform</p>
      </div>

      {/* Roadmap Button */}
      <div className="p-4 border-b border-gray-200">
        <Button 
          onClick={() => navigate('/roadmap')}
          className="w-full justify-start bg-indigo-600 hover:bg-indigo-700 text-white"
        >
          <Map className="w-4 h-4 mr-2" />
          Learning Roadmap
        </Button>
      </div>

      {/* Briefing Type Section */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={() => setBriefingSectionExpanded(!briefingSectionExpanded)}
          className="flex items-center gap-2 mb-3 w-full text-left"
        >
          {briefingSectionExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          )}
          <span className="text-sm font-medium text-gray-900">Intelligence Type</span>
        </button>
        
        {briefingSectionExpanded && (
          <div className="space-y-1">
            {briefingTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedBriefing(type.id)}
                className={`w-full flex items-center gap-3 p-2 rounded-md text-left transition-colors ${
                  selectedBriefing === type.id
                    ? 'bg-blue-50 text-blue-900 border border-blue-200'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <span className="text-sm">{type.icon}</span>
                <span className="text-sm font-medium">{type.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Date Section */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-3">
          <Calendar className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-900">Date Range</span>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <p className="text-sm text-gray-900 font-medium">{getDateRangeText(selectedBriefing)}</p>
          <p className="text-xs text-gray-500 mt-1 font-mono">
            {selectedDate.toISOString().split('T')[0]}
          </p>
        </div>
      </div>

      {/* Sources Section */}
      <div className="p-4 flex-1">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-900">Sources</span>
        </div>
        
        {/* Manual Content Entry */}
        {onManualContentAdded && (
          <ManualContentEntry onContentAdded={onManualContentAdded} />
        )}
        
        <div className="space-y-1">
          {sources.map((source) => (
            <button
              key={source.id}
              onClick={() => toggleSource(source.id)}
              className={`w-full flex items-center justify-between p-2 rounded-md text-left transition-colors ${
                selectedSources.includes(source.id) || (selectedSources.includes('all') && source.id === 'all')
                  ? 'bg-blue-50 text-blue-900 border border-blue-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-sm">{source.icon}</span>
                <span className="text-sm font-medium">{source.name}</span>
              </div>
              <span className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {source.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-gray-200">
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  );
};