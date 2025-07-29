import { Shield, TrendingUp, Globe, Cpu, AlertTriangle, CheckCircle, Clock, ExternalLink } from 'lucide-react';

interface BriefingSection {
  id: string;
  title: string;
  icon: any;
  priority: 'high' | 'medium' | 'low';
  content: {
    summary: string;
    details: string[];
    metrics?: {
      label: string;
      value: string;
      trend?: 'up' | 'down' | 'stable';
    }[];
    recommendations?: string[];
    sources?: {
      title: string;
      url: string;
      timestamp: string;
    }[];
  };
}

interface BriefingViewerProps {
  section: BriefingSection;
  className?: string;
}

export default function BriefingViewer({ section, className = "" }: BriefingViewerProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      case 'low': return 'border-green-200 bg-green-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const getPriorityTextColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-800';
      case 'medium': return 'text-yellow-800';
      case 'low': return 'text-green-800';
      default: return 'text-gray-800';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg overflow-hidden ${className}`}>
      {/* Section Header */}
      <div className={`p-6 border-b border-gray-200 ${getPriorityColor(section.priority)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <section.icon className="w-6 h-6 text-gray-700" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{section.title}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${getPriorityTextColor(section.priority)} bg-white border`}>
                  {section.priority.toUpperCase()} PRIORITY
                </span>
                <span className="text-xs text-gray-500">
                  <Clock className="w-3 h-3 inline mr-1" />
                  Last updated: {new Date().toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>
          </div>
          
          {section.priority === 'high' && (
            <AlertTriangle className="w-6 h-6 text-red-500" />
          )}
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Summary */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Summary</h3>
          <p className="text-gray-700 leading-relaxed">{section.content.summary}</p>
        </div>

        {/* Metrics */}
        {section.content.metrics && section.content.metrics.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {section.content.metrics.map((metric, index) => (
                <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-600">{metric.label}</span>
                    {metric.trend && (
                      <span className="text-lg">{getTrendIcon(metric.trend)}</span>
                    )}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Analysis */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Detailed Analysis</h3>
          <div className="space-y-3">
            {section.content.details.map((detail, index) => (
              <div key={index} className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <p className="text-gray-700 leading-relaxed">{detail}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        {section.content.recommendations && section.content.recommendations.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommendations</h3>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="space-y-2">
                {section.content.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="w-5 h-5 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5 flex-shrink-0">
                      {index + 1}
                    </span>
                    <p className="text-blue-800 text-sm leading-relaxed">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Sources */}
        {section.content.sources && section.content.sources.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Source References</h3>
            <div className="space-y-2">
              {section.content.sources.map((source, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{source.title}</p>
                    <p className="text-xs text-gray-500 font-mono">{source.timestamp}</p>
                  </div>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    View
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 