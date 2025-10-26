import uuid 
from datetime import datetime 
from typing import List , Literal , Optional , Annotated , Dict 
from operator import add 
from pydantic import BaseModel , Field , HttpUrl 
from langgraph.graph.message import AnyMessage 
from typing import TypedDict 

# --- LangGraph State --- 
class EmailState(TypedDict):
    """
        Reperesents the internal State of the LangGraph Workflow . 
        Here the 'add' reducer is crucial for merging outputs from parallel agents . 
    """
    # --- Inputs --- 
    resume_text: str 
    job_description: str 
    # --- Outputs/Accumulators --- 
    agent_responses: Annotated[List[dict],add] 
    final_email: str 
    reasoning: str 
    source_breakdown: Dict[str,str]
    # --- Metadata --- 
    job_metadata: Optional[Dict] 

# --- Metadata Schemas --- 
class UIMetadata(BaseModel):
    """
        Visual Styling metdata for Canvas UI 
    """
    color: str = Field(
        ...,
        description="Hex color code for the branch curve "
    )
    position: Literal["left","center","right"] = Field(
        ...,
        description="Position of the branch"
    )
    emoji: str = Field(
        ...,
        description="Emoji to represent the agent Card"
    )
class AgentMetadata(BaseModel):
    """
        Metadata for individual Agent Cards
    """
    word_count: int = Field(..., description="Word count of generated email")
    generation_time_ms: int = Field(..., description="Time taken to generate (milliseconds)")
    temperature: float = Field(..., description="Model temperature used")

class AggregationMetedata(BaseModel):
    """
        Aggregator performance metadata . 
    """
    word_count: int 
    generation_time_ms: int 
    quality_score: float = Field(..., ge=0, le=10, description="Quality score out of 10")

class JobMetadata(BaseModel):
    """
        Extracted job posting metadata
    """
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")

class SourceBreakdown(BaseModel):
    """
        Attribution of final email sections to source agents
    """
    subject: str = Field(..., description="Agent that contributed subject line")
    opening: str = Field(..., description="Agent that contributed opening paragraph")
    body: str = Field(..., description="Agent that contributed body content")
    closing: str = Field(..., description="Agent that contributed closing")

# --- Component Schemas --- 
class AgentDraft(BaseModel):
    """
        Individual Agent's generated Email draft
    """
    agent_name: str = Field(..., description="Agent identifier (kimi , qwen , open ai )")
    model: str = Field(...,description="Model used for generation (kimi , qwen , open ai )")
    draft: str = Field(...,description="Generated email draft")
    status: Literal["complete","processing","failed"] = Field(
        ...,
        description="Status of draft generation"
    )
    metadata: AgentMetadata 
    ui_metdata: UIMetadata 
class AggregationResult(BaseModel):
    """
        Final Synthesized email form aggregator
    """
    final_email: str = Field(... ,description="Synthesized final email")
    reasoning: str = Field(..., description="Explanation of synthesis decisions")
    metadata: AggregationMetedata 
    ui_metadata: UIMetadata = Field(..., description="Styling for the final card")
class InputContext(BaseModel):
    """
        Original Inputs for transparency 
    """
    resume_text: str = Field(..., description="Original resume text")
    job_description: str = Field(..., description="Original job description")
    job_url: HttpUrl = Field(..., description="URL of the job posting")
    job_metadata: JobMetadata = Field(..., description="Extracted job metadata")

# --- Final Response Schema ---

class EmailGenerationResponse(BaseModel):
    """
        Complete response for email generation request, matching the API contract.
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: Literal["complete", "processing", "failed"] = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    inputs: InputContext
    agent_drafts: List[AgentDraft] = Field(..., min_items=3, max_items=3)
    aggregation: AggregationResult
# --- Error Schemas ---

class ErrorDetail(BaseModel):
    """ 
        Detailed error object for 500 responses
    """
    failed_stage: str = Field(..., description="The stage of the pipeline that failed")
    error_type: str = Field(..., description="The type of the error (e.g., ModelTimeoutError)")
    message: str = Field(..., description="Detailed error message")

class InternalErrorResponse(BaseModel):
    """
        500 Internal Server Error Response
    """
    detail: str = Field("An unexpected error occurred during email generation. Please try again later.")
    error_id: str = Field(default_factory=lambda: f"err_{uuid.uuid4().hex[:8]}")
    debug_info: Optional[ErrorDetail]

class ServiceUnavailableResponse(BaseModel):
    """
        503 Service Unavailable Response
    """
    detail: str
    retry_after: int
    status_url: Optional[str]