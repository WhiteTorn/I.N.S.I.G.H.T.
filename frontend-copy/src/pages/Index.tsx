import { useState } from 'react';
import { NavigationPanel } from '@/components/NavigationPanel';
import { MainContent } from '@/components/MainContent';
import { DetailsPanel } from '@/components/DetailsPanel';
import { FocusModeToggle } from '@/components/FocusModeToggle';
import { PanelControls } from '@/components/PanelControls';

const Index = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedPost, setSelectedPost] = useState(null);
  const [selectedSources, setSelectedSources] = useState(['all']);
  const [focusMode, setFocusMode] = useState(false);
  const [showLeftPanel, setShowLeftPanel] = useState(true);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [manualContent, setManualContent] = useState([]);

  const handleManualContentAdded = (content: any) => {
    setManualContent(prev => [...prev, content]);
  };

  return (
    <div className={`min-h-screen flex w-full bg-white ${focusMode ? 'focus-mode' : ''}`}>
      <FocusModeToggle 
        focusMode={focusMode}
        onToggle={setFocusMode}
        onPanelToggle={(left, right) => {
          if (focusMode) {
            setShowLeftPanel(false);
            setShowRightPanel(false);
          } else {
            setShowLeftPanel(left);
            setShowRightPanel(right);
          }
        }}
      />
      
      <PanelControls
        showLeftPanel={showLeftPanel}
        showRightPanel={showRightPanel}
        onToggleLeft={() => setShowLeftPanel(!showLeftPanel)}
        onToggleRight={() => setShowRightPanel(!showRightPanel)}
        focusMode={focusMode}
      />

      {showLeftPanel && !focusMode && (
        <NavigationPanel 
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          selectedSources={selectedSources}
          onSourcesChange={setSelectedSources}
          onManualContentAdded={handleManualContentAdded}
        />
      )}
      
      <MainContent 
        selectedDate={selectedDate}
        selectedSources={selectedSources}
        onPostSelect={setSelectedPost}
        selectedPost={selectedPost}
        focusMode={focusMode}
        showLeftPanel={showLeftPanel}
        showRightPanel={showRightPanel}
        manualContent={manualContent}
      />
      
      {showRightPanel && !focusMode && (
        <DetailsPanel 
          selectedPost={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </div>
  );
};

export default Index;