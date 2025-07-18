import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { RoadmapProvider } from "@/contexts/RoadmapContext";
import { NotesProvider } from "@/contexts/NotesContext";
import Index from "./pages/Index";
import Roadmap from "./pages/Roadmap";
import Process from "./pages/Process";
import DailyBriefing from "./pages/DailyBriefing";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <RoadmapProvider>
      <NotesProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/roadmap" element={<Roadmap />} />
              <Route path="/process" element={<Process />} />
              <Route path="/daily-briefing" element={<DailyBriefing />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </NotesProvider>
    </RoadmapProvider>
  </QueryClientProvider>
);

export default App;