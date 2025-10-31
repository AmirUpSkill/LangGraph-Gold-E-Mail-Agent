// ============================================================
// COMPONENT: Final Email Card
// ============================================================
// Displays the synthesized final email with:
// - Quality score badge
// - Formatted email content
// - Collapsible reasoning section
// - Generation metadata
// - JSON unwrapping for clean display
// ============================================================

import { Badge } from "@/components/ui/badge";
import type { AggregationResult } from "@/types/api";
import { parseJsonWrapper } from "@/utils/textProcessing";

interface FinalEmailCardProps {
  aggregation: AggregationResult;
}

const FinalEmailCard = ({ aggregation }: FinalEmailCardProps) => {
  // --- Parse Email Content ---
  const { email, reasoning: parsedReasoning } = parseJsonWrapper(aggregation.final_email);
  const emailContent = email || aggregation.final_email;
  const reasoning = parsedReasoning || aggregation.reasoning;

  // --- Render ---
  return (
    <div className="card-3d bg-card rounded-2xl p-8 border-primary/50">
      {/* --- Card Header --- */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-14 h-14 rounded-xl bg-primary/20 flex items-center justify-center text-3xl border-2 border-primary/50">
          {aggregation.ui_metadata.emoji}
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-foreground">Final Synthesized Email</h2>
          <p className="text-sm text-muted-foreground">Aggregated from all agent drafts</p>
        </div>
        <Badge 
          className="bg-primary/20 text-primary border-primary/30"
        >
          Score: {aggregation.metadata.quality_score}/10
        </Badge>
      </div>

      {/* --- Email Content Display --- */}
      <div className="bg-secondary/30 rounded-xl p-6 mb-6 border border-border">
        <pre className="whitespace-pre-wrap text-sm text-foreground leading-relaxed font-sans">
          {emailContent}
        </pre>
      </div>

      {/* --- Synthesis Reasoning Section --- */}
      <details className="mb-4">
        <summary className="cursor-pointer text-sm font-medium text-foreground hover:text-primary transition-colors mb-2">
          View Synthesis Reasoning
        </summary>
        <div className="bg-secondary/20 rounded-lg p-4 border border-border">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {reasoning}
          </p>
        </div>
      </details>

      {/* --- Metadata Badges --- */}
      <div className="flex flex-wrap gap-2 pt-4 border-t border-border">
        <Badge variant="secondary" className="bg-secondary/50">
          {aggregation.metadata.word_count} words
        </Badge>
        <Badge variant="secondary" className="bg-secondary/50">
          {(aggregation.metadata.generation_time_ms / 1000).toFixed(1)}s generation
        </Badge>
        <Badge variant="secondary" className="bg-primary/20 text-primary border-primary/30">
          ⭐ Quality Score: {aggregation.metadata.quality_score}
        </Badge>
      </div>
    </div>
  );
};

export default FinalEmailCard;
