export interface JobMetadata {
  title: string;
  company: string;
  location: string | null;
}

export interface InputContext {
  resume_text: string;
  job_description: string;
  job_url: string;
  job_metadata: JobMetadata;
}

export interface AgentMetadata {
  word_count: number;
  generation_time_ms: number;
  temperature: number;
}

export interface UIMetadata {
  color: string;
  position: "left" | "center" | "right";
  emoji: string;
}

export interface AgentDraft {
  agent_name: string;
  model: string;
  draft: string;
  status: "complete" | "processing" | "failed";
  metadata: AgentMetadata;
  ui_metadata: UIMetadata;
}

export interface AggregationMetadata {
  word_count: number;
  generation_time_ms: number;
  quality_score: number;
}

export interface AggregationResult {
  final_email: string;
  reasoning: string;
  metadata: AggregationMetadata;
  ui_metadata: UIMetadata;
}

export interface EmailGenerationResponse {
  request_id: string;
  status: "complete" | "processing" | "failed";
  created_at: string;
  inputs: InputContext;
  agent_drafts: AgentDraft[];
  aggregation: AggregationResult;
}
