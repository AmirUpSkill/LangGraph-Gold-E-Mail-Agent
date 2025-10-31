// ============================================================
// COMPONENT: Canvas Flow
// ============================================================
// Orchestrates the visual workflow display:
// - 3D progress bar with real-time percentage
// - Agent cards arranged in grid layout
// - SVG flow lines connecting components
// - Final email card with copy functionality
// - Smooth animations and transitions
// ============================================================

import { useEffect, useState, useMemo } from "react";
import { Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { EmailGenerationResponse } from "@/types/api";
import AgentCard from "./AgentCard";
import FinalEmailCard from "./FinalEmailCard";
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard";
import { parseJsonWrapper } from "@/utils/textProcessing";

interface CanvasFlowProps {
  isGenerating: boolean;
  result: EmailGenerationResponse | null;
  progress: number;
}

const CanvasFlow = ({ isGenerating, result, progress }: CanvasFlowProps) => {
  // --- Animation State ---
  const [showAgents, setShowAgents] = useState(false);
  const [showFinal, setShowFinal] = useState(false);
  
  // --- Copy Functionality ---
  const { copied: copiedFinal, copyToClipboard } = useCopyToClipboard();

  // --- Show Agents After Delay ---
  useEffect(() => {
    if (isGenerating) {
      setShowAgents(false);
      setShowFinal(false);
      const timer = setTimeout(() => setShowAgents(true), 300);
      return () => clearTimeout(timer);
    }
  }, [isGenerating]);

  // --- Show Final After Completion ---
  useEffect(() => {
    if (result && result.status === "complete") {
      const timer = setTimeout(() => setShowFinal(true), 600);
      return () => clearTimeout(timer);
    }
  }, [result]);

  // --- Copy Final Email Handler ---
  const handleCopyFinal = () => {
    if (!result?.aggregation.final_email) return;
    
    const { email } = parseJsonWrapper(result.aggregation.final_email);
    if (email) {
      copyToClipboard(email, "Final email");
    }
  };

  // --- Early Return if No Data ---
  if (!isGenerating && !result) return null;

  // --- Memoized Agents List ---
  const agents = useMemo(() => result?.agent_drafts || [], [result]);

  // --- Render ---
  return (
    <div className="max-w-7xl mx-auto">
      <div className="relative">
        
        {/* --- SVG Flow Lines Canvas --- */}
        <svg className="absolute inset-0 w-full pointer-events-none" style={{ zIndex: 0, height: '100%', minHeight: '1400px' }}>
          
          {/* Lines from Progress Bar to Agent Cards */}
          {showAgents && agents.map((agent, idx) => {
            const positions = { left: '25%', center: '50%', right: '75%' };
            const targetX = positions[agent.ui_metadata.position];

            return (
              <path
                key={`line-to-${idx}`}
                d={`M 50% 150 Q 50% 250, ${targetX} 350`}
                className="canvas-line canvas-line-glow animate-flow-line"
                style={{
                  strokeDasharray: "1000",
                  strokeDashoffset: "1000",
                  animationDelay: `${idx * 0.2}s`,
                }}
              />
            );
          })}

          {/* Lines from Agent Cards to Final Email */}
          {showFinal && agents.map((agent, idx) => {
            const positions = { left: '25%', center: '50%', right: '75%' };
            const sourceX = positions[agent.ui_metadata.position];

            return (
              <path
                key={`line-from-${idx}`}
                d={`M ${sourceX} 800 Q ${sourceX} 950, 50% 1100`}
                className="canvas-line canvas-line-glow animate-flow-line"
                style={{
                  strokeDasharray: "1000",
                  strokeDashoffset: "1000",
                  animationDelay: `${idx * 0.2}s`,
                }}
              />
            );
          })}
        </svg>

        {/* --- 3D Progress Bar Section --- */}
        <div className="relative z-10 flex justify-center mb-32">
          <div className="w-full max-w-md">
            <div className="card-3d bg-card rounded-2xl p-8 animate-[scale-in_0.4s_ease-out]">
              <div className="space-y-4">
                
                {/* Progress Header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-foreground">
                    {progress < 100 ? 'Processing' : 'Complete'}
                  </span>
                  <span className="text-2xl font-bold text-primary">
                    {Math.round(progress)}%
                  </span>
                </div>
                
                {/* Progress Bar */}
                <div className="relative h-3 bg-secondary rounded-full overflow-hidden border-2 border-border">
                  <div 
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-primary-glow rounded-full transition-all duration-500 ease-out shadow-[0_0_20px_hsl(var(--primary)/0.5)]"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                
                {/* Status Message */}
                <p className="text-xs text-muted-foreground text-center">
                  {progress < 30 && 'Analyzing resume & job description...'}
                  {progress >= 30 && progress < 60 && 'Agents crafting personalized emails...'}
                  {progress >= 60 && progress < 90 && 'Synthesizing final output...'}
                  {progress >= 90 && progress < 100 && 'Almost there...'}
                  {progress === 100 && 'Generation complete!'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* --- Agent Drafts Grid Section --- */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 mb-32">
          {agents.map((draft, idx) => (
            <div
              key={draft.agent_name}
              className="animate-[fade-in_0.5s_ease-out,scale-in_0.5s_ease-out]"
              style={{ animationDelay: `${idx * 0.15}s`, opacity: 0, animationFillMode: 'forwards' }}
            >
              <AgentCard draft={draft} isGenerating={isGenerating && !result} />
            </div>
          ))}
        </div>

        {/* --- Final Email Section --- */}
        {showFinal && result && (
          <div className="relative z-10 flex justify-center animate-[fade-in_0.6s_ease-out,scale-in_0.6s_ease-out]">
            <div className="w-full max-w-3xl">
              <FinalEmailCard aggregation={result.aggregation} />
              
              <div className="flex justify-center mt-6">
                <Button
                  onClick={handleCopyFinal}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
                >
                  {copiedFinal ? (
                    <>
                      <Check className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy Final Email
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CanvasFlow;
