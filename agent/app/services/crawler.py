from __future__ import annotations 
import logging 
from typing import Dict , Any , Optional 
import firecrawl 
from app.core.settings import get_settings 

# --- Define Logger --- 
logger = logging.getLogger(__name__)

# --- Custom Errors --- 
class CrawlerError(RuntimeError):
    """
        Generic Crawler Failure . 
    """
class CrawlerClientError(CrawlerError):
    """
        Firecrawl Client Error . 
    """

# --- Internal Helpers --- 
def _buid_firecrawl_client() -> firecrawl.Firecrawl:
    """
        Return an authenticated FireCrawl Client
    """
    settings = get_settings()
    if not settings.firecrawl_api_key:
        raise CrawlerClientError("Firecrawl API key is not configured")
    client = firecrawl.Firecrawl(api_key=settings.firecrawl_api_key)
    return client
def _trim_markdown(md: str , max_chars: int= 50_000) -> str:
    """
        Defensive cut-off so we never blow the LLM context.
    """
    if len(md) <= max_chars:
        return md
    logger.warning("Markdown longer than %s – truncating", max_chars)
    return md[:max_chars] + "\n\n[…truncated…]"

# --- Public API To Scrap The Job  --- 
def scrape_job_page(url: str) -> Dict[str, Any]:
    """
        Scrape a job posting URL and return markdown + metadata.
    """
    client = _buid_firecrawl_client()
    logger.info("Scraping job page %s", url)
    
    try:
        result = client.scrape(
            url,
            formats=["markdown"],
            timeout=get_settings().firecrawl_timeout * 1000,
        )
    except Exception as exc:
        logger.exception("FireCrawl scrape failed for %s", url)
        raise CrawlerClientError(f"FireCrawl scrape failed: {exc}") from exc
    
    # --- Check For Any API Error --- 
    if hasattr(result, 'error') and result.error:
        logger.error("FireCrawl scrape failed for %s: %s", url, result.error)
        raise CrawlerClientError(f"FireCrawl scrape failed: {result.error}")
    
    # --- Extract the Content in Markdown --- 
    markdown = _trim_markdown(
        result.markdown if hasattr(result, 'markdown') 
        else result.get("markdown", "") if hasattr(result, 'get') 
        else ""
    )
    
    if not markdown.strip():
        raise CrawlerError("Markdown content is empty")
    
    # --- Add Some Metadata --- 
    metadata = {}
    if hasattr(result, 'metadata') and result.metadata:
        metadata = (
            result.metadata if isinstance(result.metadata, dict)
            else vars(result.metadata) if hasattr(result.metadata, '__dict__')
            else {}
        )
    
    logger.info("Scraped %s characters from %s", len(markdown), url)
    return {"markdown": markdown, "metadata": metadata}
