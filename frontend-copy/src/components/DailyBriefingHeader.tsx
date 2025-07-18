import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DailyBriefingHeader = () => {
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();

  const handleExpand = () => {
    navigate('/daily-briefing');
  };

  return (
    <section className="daily-briefing-header mb-8">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <button
          onClick={handleExpand}
          className="w-full flex items-center justify-between text-left group"
        >
          <h2 className="flex items-center gap-3 text-xl font-semibold text-gray-900">
            <span className="text-2xl">📊</span>
            Full Daily Briefing
          </h2>
          <div className="flex items-center gap-2 text-sm text-gray-600 group-hover:text-blue-600">
            <span>Expand</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        </button>
        
        <div className="mt-4">
          <p className="text-lg text-gray-700 leading-relaxed">
            Today's intelligence indicates significant movement in three key areas: 
            cryptocurrency regulation shifts across major markets, emerging 
            geopolitical alliances in Southeast Asia, and breakthrough developments 
            in quantum computing infrastructure.
          </p>
          
          <div className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-white rounded border border-blue-100">
                <h3 className="font-medium text-gray-900 mb-2">🔐 Technology Sector</h3>
                <p className="text-sm text-gray-600">Regulatory frameworks for crypto showing coordinated policy shifts</p>
              </div>
              <div className="p-4 bg-white rounded border border-blue-100">
                <h3 className="font-medium text-gray-900 mb-2">🌏 Geopolitics</h3>
                <p className="text-sm text-gray-600">Southeast Asian alliance patterns indicate strategic realignment</p>
              </div>
              <div className="p-4 bg-white rounded border border-blue-100">
                <h3 className="font-medium text-gray-900 mb-2">💰 Economics</h3>
                <p className="text-sm text-gray-600">Central bank policy coordination across major economies</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};