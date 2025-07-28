import { Link } from 'react-router-dom';
import { useState } from 'react';

export default function DailyBriefing() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [briefingData, setBriefingData] = useState<string | null>(null);

  const handleGenerateBriefing = async () => {
    setIsGenerating(true);
    // TODO: Connect to backend API
    try {
      // Placeholder - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      setBriefingData(`Daily Intelligence Briefing for ${selectedDate}\n\n• Market Analysis: Sample data\n• Security Updates: Sample data\n• Technology Trends: Sample data`);
    } catch (error) {
      console.error('Failed to generate briefing:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Navigation Panel */}
      <div className="w-80 bg-card border-r border-border p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">INSIGHT</h1>
          <p className="text-sm text-muted-foreground">Intelligence Platform</p>
        </div>
        
        <div className="space-y-4">
          <Link 
            to="/" 
            className="block w-full p-3 bg-secondary text-secondary-foreground rounded-lg text-center hover:bg-secondary/90 transition-colors"
          >
            ← Back to Dashboard
          </Link>
          
          <div className="bg-primary/10 p-3 rounded-lg">
            <p className="text-sm text-muted-foreground">Daily Briefing Generator</p>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Daily Intelligence Briefing</h2>
          <p className="text-muted-foreground mb-6">
            Generate AI-powered intelligence briefings from multiple sources for any date.
          </p>
          
          {/* Controls */}
          <div className="bg-card p-6 rounded-lg border border-border mb-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <label htmlFor="date" className="block text-sm font-medium mb-2">
                  Select Date
                </label>
                <input
                  type="date"
                  id="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full p-2 border border-border rounded-md bg-background"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleGenerateBriefing}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? 'Generating...' : 'Generate Briefing'}
                </button>
              </div>
            </div>
          </div>
          
          {/* Briefing Output */}
          <div className="bg-card p-6 rounded-lg border border-border">
            <h3 className="text-xl font-semibold mb-4">Intelligence Briefing</h3>
            {isGenerating ? (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-3 text-muted-foreground">Analyzing intelligence sources...</span>
              </div>
            ) : briefingData ? (
              <div className="space-y-4">
                <pre className="whitespace-pre-wrap text-sm bg-secondary/20 p-4 rounded-md border">
                  {briefingData}
                </pre>
                <div className="flex justify-end">
                  <button className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors">
                    Export Briefing
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground text-center p-8">
                <p>Select a date and click "Generate Briefing" to create your intelligence report.</p>
              </div>
            )}
          </div>
          
          {/* Status */}
          <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">
              🔧 Ready for backend integration - API endpoints to be connected
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 