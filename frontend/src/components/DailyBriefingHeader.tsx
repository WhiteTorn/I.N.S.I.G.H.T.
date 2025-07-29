import { useState } from 'react';
import { BarChart3, Expand, Shield, TrendingUp, Globe, Cpu } from 'lucide-react';

export default function DailyBriefingHeader() {
  const [isExpanded, setIsExpanded] = useState(false);

  const summaryItems = [
    {
      icon: Shield,
      title: '🔐 Technology Sector',
      description: 'Major security vulnerabilities discovered in popular frameworks. Enterprise adoption of AI tools continues.',
      color: 'text-blue-600'
    },
    {
      icon: TrendingUp,
      title: '📈 Market Analysis',
      description: 'Tech stocks showing resilience amid economic uncertainty. Crypto markets experiencing volatility.',
      color: 'text-green-600'
    },
    {
      icon: Globe,
      title: '🌍 Geopolitical Events',
      description: 'Trade tensions affecting supply chains. New regulations on data privacy emerging globally.',
      color: 'text-purple-600'
    },
    {
      icon: Cpu,
      title: '🤖 AI & Innovation',
      description: 'Breakthrough in quantum computing announced. Major AI companies forming strategic partnerships.',
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="mb-8">
      {/* Predictive Thread Alert */}
      <div className="predictive-thread-alert p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-full">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Predictive Intelligence Thread</h3>
              <p className="text-sm text-gray-600">AI-generated connections across multiple data sources</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Live Analysis</span>
          </div>
        </div>
        
        <div className="bg-white/50 rounded-lg p-4 border border-blue-200">
          <p className="text-sm text-gray-800 leading-relaxed">
            <strong>Emerging Pattern:</strong> Increased cybersecurity investments correlating with AI adoption rates. 
            Companies implementing AI tools are simultaneously increasing security budgets by 40% on average. 
            This trend suggests a reactive security posture rather than proactive integration.
          </p>
        </div>
      </div>

      {/* Daily Briefing Header */}
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">📊 Full Daily Briefing</h2>
                <p className="text-sm text-gray-600">
                  {new Date().toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200"
            >
              <Expand className="w-4 h-4" />
              <span className="text-sm font-medium">
                {isExpanded ? 'Collapse' : 'Expand'}
              </span>
            </button>
          </div>
        </div>

        {/* Summary Grid */}
        {isExpanded && (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {summaryItems.map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors duration-200"
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg bg-white border`}>
                      <item.icon className={`w-4 h-4 ${item.color}`} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-1">{item.title}</h4>
                      <p className="text-sm text-gray-600 leading-relaxed">{item.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  Last updated: {new Date().toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    timeZoneName: 'short'
                  })}
                </div>
                <div className="flex items-center gap-2">
                  <button className="action-btn bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100">
                    Export Report
                  </button>
                  <button className="action-btn bg-green-50 text-green-700 border border-green-200 hover:bg-green-100">
                    Share Briefing
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 