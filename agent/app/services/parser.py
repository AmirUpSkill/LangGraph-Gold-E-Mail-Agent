import io, logging ,httpx 
from typing import Final 
from app.core.settings import get_settings

# --- Logger ---
logger = logging.getLogger(__name__)
# --- Define API Data --- 
URL: Final = "https://api.va.landing.ai/v1/ade/parse"
MODEL: Final = "dpt-2-latest"
MAX_CHARS: Final = 50_000

# --- Define Custom Exception --- 
class ParserError(Exception):
    """
        Custom Exception for Landing AI Parser Errors
    """
class ParserClientError(ParserError):
    """
        Custom Exception for Landing AI Parser Client Errors
    """
class ParserValidationError(ParserError):
    """
        Custom Exception for Landing AI Parser Validation Errors
    """
class ParserEmptyError(ParserError):
    """
        Custom Exception for Landing AI Parser Empty Errors
    """

# --- Here We define the Logic --- 
def parse_resume(content: bytes) -> str:
    """
        Resume Bytes -> Clean text via Landing AI ADE 
    """
    settings = get_settings()
    # --- Check Length --- 
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise ParserValidationError(
            f"Resume size exceeds {settings.max_upload_size_mb}MB limit"
        )
    if not (key := settings.landing_ai_api_key):
        logger.warning("No LANDING_AI_API_KEY – using dummy text")
        return "John Developer\nSenior Software Engineer\nReact | TypeScript | Node.js"
    # --- Call the API --- 
    with httpx.Client(timeout=settings.landing_ai_timeout) as client:
        response = client.post(
            URL,
            files={"document":("resume.pdf",io.BytesIO(content), "application/pdf")},
            data={"model":MODEL},
            headers={
                "Authorization":f"Bearer {key}"
            }
        )
        # --- Handle Response --- 
        if response.is_error:
            raise ParserClientError(
                f"API Error: {response.status_code} - {response.text}"
            )
        
        payload=response.json()
        text=payload.get("markdown","").strip()
        if not text:
            raise ParserEmptyError("Empty response from Landing AI API")
        # --- Validate Text Length ---
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "\n[Truncated]"

        logger.info("Parsed %s pages in %sms (credits %s)",
                    payload["metadata"]["page_count"],
                    payload["metadata"]["duration_ms"],
                    payload["metadata"]["credit_usage"])
        return text 

