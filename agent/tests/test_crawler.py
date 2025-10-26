"""
Test suite for app.services.crawler module.

Tests cover:
1. Successful scraping of job pages
2. Error handling for various failure scenarios
3. Markdown trimming functionality
4. API key validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from app.services.crawler import (
    scrape_job_page,
    CrawlerError,
    CrawlerClientError,
    _buid_firecrawl_client,
    _trim_markdown,
)


class TestTrimMarkdown:
    """Test the _trim_markdown utility function."""

    def test_trim_markdown_within_limit(self):
        """Test markdown that doesn't exceed limit is returned as-is."""
        text = "Hello " * 100  # Short text
        result = _trim_markdown(text)
        assert result == text
        assert len(result) < 50_000

    def test_trim_markdown_exceeds_limit(self):
        """Test markdown that exceeds limit is truncated with marker."""
        text = "x" * 60_000  # Exceed default 50k limit
        result = _trim_markdown(text)
        assert len(result) < 60_000
        assert "[…truncated…]" in result
        assert result.startswith("x" * 50_000)

    def test_trim_markdown_custom_limit(self):
        """Test trim with custom character limit."""
        text = "x" * 1000
        result = _trim_markdown(text, max_chars=500)
        assert len(result) <= 500 + len("\n\n[…truncated…]")
        assert "[…truncated…]" in result


class TestBuildFirecrawlClient:
    """Test the _buid_firecrawl_client factory function."""

    @patch("app.services.crawler.get_settings")
    @patch("app.services.crawler.firecrawl.Firecrawl")
    def test_build_client_success(self, mock_firecrawl_class, mock_get_settings):
        """Test successful client creation with valid API key."""
        mock_settings = Mock()
        mock_settings.firecrawl_api_key = "fc-test-api-key-123"
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_firecrawl_class.return_value = mock_client

        result = _buid_firecrawl_client()

        assert result == mock_client
        mock_firecrawl_class.assert_called_once_with(api_key="fc-test-api-key-123")

    @patch("app.services.crawler.get_settings")
    def test_build_client_missing_api_key(self, mock_get_settings):
        """Test client creation fails when API key is missing."""
        mock_settings = Mock()
        mock_settings.firecrawl_api_key = None
        mock_get_settings.return_value = mock_settings

        with pytest.raises(CrawlerClientError) as exc_info:
            _buid_firecrawl_client()

        assert "Firecrawl API key is not configured" in str(exc_info.value)

    @patch("app.services.crawler.get_settings")
    def test_build_client_empty_api_key(self, mock_get_settings):
        """Test client creation fails when API key is empty string."""
        mock_settings = Mock()
        mock_settings.firecrawl_api_key = ""
        mock_get_settings.return_value = mock_settings

        with pytest.raises(CrawlerClientError) as exc_info:
            _buid_firecrawl_client()

        assert "Firecrawl API key is not configured" in str(exc_info.value)


class TestScrapeJobPage:
    """Test the main scrape_job_page function."""

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_success(self, mock_get_settings, mock_build_client):
        """Test successful scraping of a job page."""
        # Setup mock settings
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        # Setup mock FireCrawl client
        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock the Document object response (not dict)
        mock_response = Mock()
        mock_response.markdown = "# Senior Frontend Engineer\n\nWe're looking for..."
        mock_response.metadata = {"title": "Senior Frontend Engineer", "description": "Join our team"}
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        # Call the function
        url = "https://jobs.lever.co/mistral/e76d2957-2bf6-4d8f-90a2-29bf9a927823"
        result = scrape_job_page(url)

        # Assertions
        assert result["markdown"] == "# Senior Frontend Engineer\n\nWe're looking for..."
        assert result["metadata"]["title"] == "Senior Frontend Engineer"
        mock_client.scrape.assert_called_once_with(
            url,
            formats=["markdown"],
            timeout=60_000,  # 60 seconds * 1000
        )

    @patch("app.services.crawler._buid_firecrawl_client")
    def test_scrape_client_exception(self, mock_build_client):
        """Test error handling when FireCrawl client raises exception."""
        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock exception from FireCrawl
        mock_client.scrape.side_effect = Exception("Network timeout")

        url = "https://example.com"
        with pytest.raises(CrawlerClientError) as exc_info:
            scrape_job_page(url)

        assert "FireCrawl scrape failed: Network timeout" in str(exc_info.value)

    @patch("app.services.crawler._buid_firecrawl_client")
    def test_scrape_api_failure_response(self, mock_build_client):
        """Test error handling when FireCrawl API returns error."""
        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object with error
        mock_response = Mock()
        mock_response.error = "Invalid URL or access denied"
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        with pytest.raises(CrawlerClientError) as exc_info:
            scrape_job_page(url)

        assert "Invalid URL or access denied" in str(exc_info.value)

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_empty_markdown(self, mock_get_settings, mock_build_client):
        """Test error handling when scraped content is empty."""
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object with empty markdown
        mock_response = Mock()
        mock_response.markdown = ""
        mock_response.metadata = {"title": "Test Page"}
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        with pytest.raises(CrawlerError) as exc_info:
            scrape_job_page(url)

        assert "Markdown content is empty" in str(exc_info.value)

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_whitespace_only_markdown(
        self, mock_get_settings, mock_build_client
    ):
        """Test error handling when markdown contains only whitespace."""
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object with whitespace-only markdown
        mock_response = Mock()
        mock_response.markdown = "   \n\n  \t  "
        mock_response.metadata = {"title": "Test Page"}
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        with pytest.raises(CrawlerError) as exc_info:
            scrape_job_page(url)

        assert "Markdown content is empty" in str(exc_info.value)

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_large_markdown_trimmed(self, mock_get_settings, mock_build_client):
        """Test that large markdown is properly trimmed."""
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object with very large markdown
        huge_content = "x" * 60_000
        mock_response = Mock()
        mock_response.markdown = huge_content
        mock_response.metadata = {"title": "Large Page"}
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        result = scrape_job_page(url)

        # Should be trimmed
        assert len(result["markdown"]) < 60_000
        assert "[…truncated…]" in result["markdown"]

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_missing_metadata(self, mock_get_settings, mock_build_client):
        """Test handling when metadata is missing from response."""
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object without metadata
        mock_response = Mock()
        mock_response.markdown = "# Job Title\nThis is the job description."
        mock_response.metadata = None  # No metadata
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        result = scrape_job_page(url)

        assert result["markdown"] == "# Job Title\nThis is the job description."
        assert result["metadata"] == {}  # Default empty dict

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_scrape_timeout_configuration(self, mock_get_settings, mock_build_client):
        """Test that timeout is correctly passed to FireCrawl."""
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 120  # 2 minutes
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Mock Document object
        mock_response = Mock()
        mock_response.markdown = "Test content"
        mock_response.metadata = {}
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        url = "https://example.com"
        scrape_job_page(url)

        # Verify timeout was converted to milliseconds
        mock_client.scrape.assert_called_once()
        call_kwargs = mock_client.scrape.call_args.kwargs
        assert call_kwargs["timeout"] == 120_000  # 120 * 1000


class TestIntegration:
    """Integration tests (mock-light) for the crawler module."""

    @patch("app.services.crawler._buid_firecrawl_client")
    @patch("app.services.crawler.get_settings")
    def test_end_to_end_job_scraping(self, mock_get_settings, mock_build_client):
        """Test complete job scraping workflow."""
        # Setup
        mock_settings = Mock()
        mock_settings.firecrawl_timeout = 60
        mock_get_settings.return_value = mock_settings

        mock_client = Mock()
        mock_build_client.return_value = mock_client

        # Realistic job posting response
        job_content = """
# Senior Frontend Engineer

## About the Role
We're looking for an experienced frontend engineer to join our team.

## Responsibilities
- Build scalable React applications
- Mentor junior developers
- Contribute to design system

## Requirements
- 5+ years with React
- Strong TypeScript skills
- Experience with Next.js

## Nice to Have
- GraphQL experience
- Open source contributions
        """

        # Mock Document object
        mock_response = Mock()
        mock_response.markdown = job_content
        mock_response.metadata = {
            "title": "Senior Frontend Engineer",
            "description": "Join our growing team",
            "sourceURL": "https://jobs.lever.co/example/123",
            "statusCode": 200,
        }
        mock_response.error = None
        mock_client.scrape.return_value = mock_response

        # Execute
        url = "https://jobs.lever.co/example/123"
        result = scrape_job_page(url)

        # Verify
        assert "Senior Frontend Engineer" in result["markdown"]
        assert "React" in result["markdown"]
        assert result["metadata"]["title"] == "Senior Frontend Engineer"
        assert result["metadata"]["statusCode"] == 200
