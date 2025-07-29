import React from 'react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { ChevronLeft, Download, Share2, Calendar, Clock, BarChart3, TrendingUp, Shield, Globe, Cpu, RefreshCw } from 'lucide-react';

export default function DailyBriefing() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeSection, setActiveSection] = useState('executive-summary');

  const handleGenerateBriefing = async () => {
    setIsGenerating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000));
    } catch (error) {
      console.error('Failed to generate briefing:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const briefingSections = [
    { id: 'executive-summary', title: 'Executive Summary', icon: BarChart3 },
    { id: 'technology', title: 'Technology Sector', icon: Cpu },
    { id: 'security', title: 'Security Updates', icon: Shield },
    { id: 'markets', title: 'Market Analysis', icon: TrendingUp },
    { id: 'geopolitical', title: 'Geopolitical Events', icon: Globe }
  ];

  const executiveSummary = {
    keyInsights: [
      "Major security vulnerability discovered in popular React ecosystem affecting 2M+ weekly downloads",
      "AI development tools showing 30-40% productivity improvements in enterprise environments",
      "TypeScript performance optimization discussions trending in developer communities",
      "Cybersecurity investments correlating directly with AI adoption rates across industries"
    ],
    threatLevel: "Medium",
    opportunities: 3,
    criticalUpdates: 2
  };

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
                className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-lg bg-white text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors"
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
          </div>
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
            <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <Download className="w-4 h-4" />
              Export PDF
            </button>
            <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <Share2 className="w-4 h-4" />
              Share Briefing
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
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-green-700">Live</span>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>🎯 Threat Level: <strong className="text-yellow-600">Medium</strong></span>
                <span>📊 Sources: <strong>47</strong></span>
                <span>🔄 Updates: <strong>12</strong></span>
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
                    <div className="text-2xl font-bold text-red-600">{executiveSummary.criticalUpdates}</div>
                    <p className="text-xs text-gray-500 mt-1">Requiring immediate attention</p>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Opportunities</h3>
                    </div>
                    <div className="text-2xl font-bold text-green-600">{executiveSummary.opportunities}</div>
                    <p className="text-xs text-gray-500 mt-1">Strategic opportunities identified</p>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-yellow-100 rounded-lg">
                        <BarChart3 className="w-5 h-5 text-yellow-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Threat Level</h3>
                    </div>
                    <div className="text-2xl font-bold text-yellow-600">{executiveSummary.threatLevel}</div>
                    <p className="text-xs text-gray-500 mt-1">Overall assessment</p>
                  </div>
                </div>

                {/* Key Insights */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                  <div className="space-y-3">
                    {executiveSummary.keyInsights.map((insight, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                          {index + 1}
                        </div>
                        <p className="text-gray-800 leading-relaxed">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Section Content Placeholder */}
          {activeSection !== 'executive-summary' && (
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
                This section will contain detailed analysis and intelligence for {briefingSections.find(s => s.id === activeSection)?.title.toLowerCase()}.
              </p>
              <div className="inline-flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-4 py-2 rounded-lg">
                <RefreshCw className="w-4 h-4" />
                Ready for backend integration
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 