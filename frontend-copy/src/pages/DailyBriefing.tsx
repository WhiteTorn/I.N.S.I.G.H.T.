import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

const DailyBriefing = () => {
  const navigate = useNavigate();
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const briefingSections = [
    {
      id: 'technology',
      title: 'Technology Sector',
      subtitle: 'Companies, Funding, and Legal',
      items: [
        {
          title: 'Telegram Web3 Development Breakthrough',
          content: 'Pavel Durov announces Telegram\'s new "Gifts" feature has processed over $10M in transactions within first week. Platform introducing animated collectibles as digital assets, signaling major push into Web3 economy while maintaining user privacy standards.',
          sources: ['@durov on Telegram', 'Telegram Official Blog'],
          originalContent: `Telegram Gifts are here! 🎁

We've just launched a new way to surprise your friends with collectible gifts. Each gift is a unique digital collectible that lives on the blockchain.

In just one week:
- Over 500,000 gifts sent
- $10M+ in transactions
- 50+ unique designs released

What makes Telegram Gifts special:
1. True ownership - stored on TON blockchain
2. Limited editions increase in value
3. Can be displayed on profiles
4. Transferable between users

This is just the beginning of Telegram's Web3 journey. Privacy-first, user-owned digital economy is our vision for the future.

Try sending a gift today! Link: t.me/gifts`
        },
        {
          title: 'Google Quantum Computing Milestone',
          content: 'Veritasium explores breakthrough in quantum error correction at Google\'s quantum lab. New "Willow" chip demonstrates exponential error reduction with scale, solving 30-year challenge in quantum computing.',
          sources: ['Veritasium YouTube', 'Google AI Blog'],
          originalContent: `[Video Transcript - 00:00:00 to 00:15:32]

Derek: Today I'm at Google's quantum AI lab in Santa Barbara, and they've just achieved something that many thought was impossible...

[00:01:15] Hartmut Neven: "What we've demonstrated with Willow is that as we add more qubits, we actually reduce errors exponentially. This is the breakthrough we've been working toward for decades."

[00:03:42] The key insight is something called "surface codes." Imagine you have information spread across multiple qubits in a way that errors can be detected and corrected without destroying the quantum state...

[00:07:23] To put this in perspective, we ran a benchmark calculation that would take the world's fastest supercomputer 10 septillion years. Willow completed it in under 5 minutes...`
        }
      ]
    },
    {
      id: 'geopolitics',
      title: 'Geopolitical Developments',
      subtitle: 'Southeast Asian Alliance Patterns',
      items: [
        {
          title: 'Strategic Realignment in Southeast Asia',
          content: 'Intelligence indicates emerging geopolitical alliances in Southeast Asia showing coordinated policy shifts across major economies, suggesting strategic realignment in regional power dynamics.',
          sources: ['Regional Intelligence Reports', 'Policy Analysis Centers'],
          originalContent: `CLASSIFIED BRIEFING - SOUTHEAST ASIA REGIONAL ANALYSIS

Executive Summary:
Recent diplomatic movements across ASEAN member states indicate a coordinated shift in regional alliance structures. Key indicators include:

1. Joint Economic Initiatives
- Coordinated currency stabilization measures
- Shared infrastructure development projects
- Technology transfer agreements

2. Security Cooperation
- Enhanced maritime patrol coordination
- Intelligence sharing protocols
- Joint military exercises

3. Policy Alignment
- Synchronized trade policy announcements
- Coordinated response to external economic pressures
- Unified stance on regional security issues

Assessment: These developments suggest a maturing regional bloc with increased autonomy in global affairs.`
        }
      ]
    },
    {
      id: 'economics',
      title: 'Economic Intelligence',
      subtitle: 'Central Bank Coordination & Crypto Regulation',
      items: [
        {
          title: 'Coordinated Central Bank Policy Shifts',
          content: 'Central bank policy coordination across major economies showing unprecedented synchronization in monetary policy, particularly regarding digital currency frameworks and regulatory approaches.',
          sources: ['Federal Reserve Communications', 'ECB Policy Papers', 'Bank of Japan Statements'],
          originalContent: `ECONOMIC INTELLIGENCE DIGEST

Cross-Border Monetary Policy Coordination:

Federal Reserve (US):
- Digital dollar pilot program expansion
- New framework for cryptocurrency regulation
- Coordination protocols with international counterparts

European Central Bank:
- Digital euro implementation timeline accelerated
- Unified approach to stablecoin regulation
- Cross-border payment infrastructure development

Bank of Japan:
- Digital yen research phase completion
- Partnership agreements for international digital currency testing
- Regulatory sandbox expansion for fintech innovation

Analysis: Unprecedented level of coordination suggests preparation for major shift in global monetary infrastructure.`
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white flex">
      {/* Table of Contents */}
      <div className="w-80 bg-gray-50 border-r border-gray-200 p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Intelligence
          </Button>
          <h2 className="text-lg font-semibold text-gray-900">Daily Briefing</h2>
          <p className="text-sm text-gray-600">June 25, 2025</p>
        </div>

        <nav className="space-y-2">
          {briefingSections.map((section) => (
            <div key={section.id}>
              <button
                onClick={() => {
                  const element = document.getElementById(section.id);
                  element?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-gray-100 transition-colors"
              >
                <div className="font-medium text-gray-900">{section.title}</div>
                <div className="text-xs text-gray-500">{section.items.length} items</div>
              </button>
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Presidential Daily Briefing
            </h1>
            <p className="text-lg text-gray-600">
              June 25, 2025 • Comprehensive Intelligence Summary
            </p>
          </div>

          {/* Executive Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Executive Summary</h2>
            <p className="text-gray-700 leading-relaxed">
              Today's intelligence indicates significant movement in three key areas: 
              breakthrough developments in quantum computing infrastructure, emerging 
              geopolitical alliances in Southeast Asia, and coordinated cryptocurrency 
              regulation shifts across major markets. These developments suggest a 
              convergence of technological advancement and policy coordination that 
              may reshape global economic and security landscapes.
            </p>
          </div>

          {/* Briefing Sections */}
          {briefingSections.map((section) => (
            <section key={section.id} id={section.id} className="mb-12">
              <div className="border-b border-gray-200 pb-4 mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">{section.title}</h2>
                <p className="text-gray-600 mt-1">{section.subtitle}</p>
              </div>

              <div className="space-y-6">
                {section.items.map((item, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      {item.title}
                    </h3>
                    
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {item.content}
                    </p>

                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-sm text-gray-500">
                        <span className="font-medium">Sources:</span> {item.sources.join(', ')}
                      </div>
                    </div>

                    <button
                      onClick={() => toggleSection(`${section.id}-${index}`)}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {expandedSections[`${section.id}-${index}`] 
                        ? 'Hide original content' 
                        : 'Show original content'
                      }
                    </button>

                    {expandedSections[`${section.id}-${index}`] && (
                      <div className="mt-4 bg-gray-50 border border-gray-200 rounded p-4">
                        <h4 className="font-medium text-gray-900 mb-2">Original Content</h4>
                        <div className="text-sm text-gray-700 whitespace-pre-line">
                          {item.originalContent}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DailyBriefing;