// ============================================================
// COMPONENT: Agent Card
// ============================================================
// Displays individual AI agent's email draft with:
// - Agent identity (name, emoji, model)
// - Loading state during generation
// - Draft content with cleaned output
// - Copy to clipboard functionality
// - Metadata badges (word count, generation time, temperature)
// ============================================================

import { Copy, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { AgentDraft } from "@/types/api";
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard";
import { removeThinkTags } from "@/utils/textProcessing";

interface AgentCardProps {
  draft: AgentDraft;
  isGenerating: boolean;
}

const AgentCard = ({ draft, isGenerating }: AgentCardProps) => {
  // --- Copy Functionality ---
  const { copied, copyToClipboard } = useCopyToClipboard();

  // --- Clean Draft Content ---
  const cleanDraft = removeThinkTags(draft.draft);

  // --- Copy Handler ---
  const handleCopy = () => {
    copyToClipboard(cleanDraft, `${draft.agent_name} draft`);
  };

  // --- Render ---
  return (
    <div 
      className="card-3d bg-card rounded-2xl p-6 hover:scale-[1.02] transition-all duration-300"
      style={{ 
        borderColor: draft.ui_metadata.color,
        borderWidth: '2px'
      }}
    >
      {/* --- Card Header --- */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-xl flex items-center justify-center text-2xl"
            style={{ backgroundColor: `${draft.ui_metadata.color}20` }}
          >
            {draft.ui_metadata.emoji}
          </div>
          <div>
            <h3 className="font-semibold text-foreground capitalize">{draft.agent_name}</h3>
            <p className="text-xs text-muted-foreground">{draft.model}</p>
          </div>
        </div>
        
        {draft.status === "complete" && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-8 w-8 p-0"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </Button>
        )}
      </div>

      {/* --- Draft Content --- */}
      <div className="mb-4">
        {isGenerating || draft.status === "processing" ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Generating draft...</p>
          </div>
        ) : draft.status === "failed" ? (
          <div className="py-8 text-center">
            <p className="text-destructive">Generation failed</p>
          </div>
        ) : (
          <div className="prose prose-sm prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-foreground leading-relaxed font-sans">
              {cleanDraft}
            </pre>
          </div>
        )}
      </div>

      {/* --- Metadata Badges --- */}
      {draft.status === "complete" && (
        <div className="flex flex-wrap gap-2 pt-4 border-t border-border">
          <Badge variant="secondary" className="bg-secondary/50">
            {draft.metadata.word_count} words
          </Badge>
          <Badge variant="secondary" className="bg-secondary/50">
            {(draft.metadata.generation_time_ms / 1000).toFixed(1)}s
          </Badge>
          <Badge variant="secondary" className="bg-secondary/50">
            temp: {draft.metadata.temperature}
          </Badge>
        </div>
      )}
    </div>
  );
};

export default AgentCard;
