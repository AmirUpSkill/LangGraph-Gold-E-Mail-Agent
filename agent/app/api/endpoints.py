import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl, ValidationError
from typing import Dict, Any

from app.core.schemas import (
    EmailGenerationResponse, 
    EmailState,
    InternalErrorResponse,
    ServiceUnavailableResponse,
    InputContext,
    JobMetadata,
    AgentDraft,
    AggregationResult,
    SourceBreakdown,
    AggregationMetedata,
    UIMetadata,
    ErrorDetail
)
from app.core.settings import get_settings
from app.services.parser import parse_resume, ParserError, ParserValidationError, ParserClientError
from app.services.crawler import scrape_job_page, CrawlerError, CrawlerClientError
from app.services.llm_factory import LLMFactoryError
from app.core.graph import email_graph 

# --- SetUp Router --- 
router = APIRouter()
# --- SetUp Logger --- 
logger = logging.getLogger(__name__)
# --- SetUp settings --- 
settings = get_settings()


@router.post(
    "/generate-email",
    response_model = EmailGenerationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ServiceUnavailableResponse},
        status.HTTP_400_BAD_REQUEST: {"model": Dict[str, Any]},
    }
)
async def generate_email(
    job_url: HttpUrl = Form(
        ...,
        description="URL of the Job Posting"
    ),
    resume: UploadFile = File(
        ...,
        description="Resume File in PDF or DOCX format"
    )
): 
    """
        Here We Will try to Generate a Cold Email Using Multi-Agent Branching And Aggregation . 
    """
    # --- Generate The Request Id --- 
    request_id = str(uuid.uuid4())
    logger.info(f"Starting email generation for request_id: {request_id}")
    # --- Let's Validate the Input --- 
    try:
        # --- Check the File Size --- 
        if resume.size is not None and resume.size > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB."
            )
        # --- Now Let's Read the File Content --- 
        resume_bytes = await resume.read()
        # --- Let's Call the Services Need it here --- 
        logger.info("Parsing resume with Landing AI for %s" , request_id)
        resume_text = parse_resume(resume_bytes)

        # --- Let's Scrap the Job Description --- 
        logger.info("Scraping Job URL with FireCrawl for %s", request_id)
        crawler_result = scrape_job_page(str(job_url))
        # --- Let's Get the Job Description --- 
        job_description = crawler_result["markdown"]
        job_metadata = crawler_result["metadata"]
    except (ParserValidationError, CrawlerError) as e:
        logger.error("Validation/Service Error for %s: %s", request_id, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except (ParserClientError, CrawlerClientError) as e:
        logger.error("External Service Error for %s: %s", request_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required external service (FireCrawl/Landing AI) failed to process the request."
        )

    except Exception as e:
        logger.error("Unexpected Error during pre-processing for %s: %s", request_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during input processing. Please check the URL and file.",
        )
    # --- Let's thing About the LangGraph Execution (The Full Agentic Workflow ) --- 
    try:
        # --- Initialize LangGraph State --- 
        initial_state: EmailState = {
            "resume_text": resume_text,
            "job_description": job_description,
            "job_metadata": job_metadata,
            "agent_responses": [],
            "final_email": "",
            "reasoning": "",
            "source_breakdown": {},
        }
        # --- Let's Invoke the Compiled Graph --- 
        result: EmailState = email_graph.invoke(initial_state)
        # --- Extract and parse Job Metadata ---
        raw_job_metadata = job_metadata or {}
        parsed_job_metadata = JobMetadata(
            title=raw_job_metadata.get("title", raw_job_metadata.get("ogTitle", "Unknown Position")),
            company=raw_job_metadata.get("company", raw_job_metadata.get("ogSiteName", "Unknown Company")),
            location=raw_job_metadata.get("location")
        )
        # --- Parse Agent Drafts to AgentDraft Models --- 
        parsed_agent_drafts = [
            AgentDraft(**draft) for draft in result["agent_responses"]
        ]
        # --- Parse Source Breakdown --- 
        raw_breakdown = result.get("source_breakdown", {})
        parsed_breakdown = SourceBreakdown(
            subject=raw_breakdown.get("subject", "kimi"),
            opening=raw_breakdown.get("opening", "kimi"),
            body=raw_breakdown.get("body", "qwen"),
            closing=raw_breakdown.get("closing", "openai_oss")
        )

        response_data = EmailGenerationResponse(
            request_id=request_id,
            status="complete",
            inputs=InputContext(
                resume_text=resume_text,
                job_description=job_description,
                job_url=job_url,
                job_metadata=parsed_job_metadata
            ),
            agent_drafts=parsed_agent_drafts,
            aggregation=AggregationResult(
                final_email=result["final_email"],
                reasoning=result["reasoning"],
                source_breakdown=parsed_breakdown,
                metadata=AggregationMetedata(
                    word_count=len(result["final_email"].split()),
                    generation_time_ms=0,  
                    quality_score=8.5  
                ),
                ui_metadata=UIMetadata(
                    color="#C0C0C0",
                    position="center",
                    emoji="💎"
                )
            )
        )
        
        logger.info("Email generation complete for %s", request_id)
        return response_data

    except Exception as e:
        error_id = f"err_{uuid.uuid4().hex[:8]}"
        logger.error("LangGraph Execution Failed for %s (Error ID: %s): %s", request_id, error_id, str(e), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=InternalErrorResponse(
                detail="An unexpected error occurred during the AI generation pipeline. Please contact support.",
                error_id=error_id,
                debug_info=ErrorDetail(
                    failed_stage="langgraph_execution",
                    error_type=type(e).__name__,
                    message=str(e)
                )
            ).model_dump()
        )
