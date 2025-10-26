"""
Smoke Test: Real FireCrawl Integration Test

This test scrapes an actual job posting URL and displays the results.
Requires valid FIRECRAWL_API_KEY in .env

Run with: pytest tests/test_crawler_smoke.py -v -s
"""

import pytest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import json
from app.services.crawler import scrape_job_page, CrawlerError
from app.core.settings import get_settings

# Initialize Rich console for beautiful output
console = Console()


@pytest.mark.integration
def test_scrape_lever_job_posting():
    """
    Smoke test: Scrape a real job posting from Lever.
    
    This test:
    1. Attempts to scrape the actual Lever job posting URL
    2. Validates the response structure
    3. Displays formatted output using Rich
    """
    
    # Test URL - Mistral AI Senior Backend Engineer role
    job_url = "https://jobs.lever.co/mistral/e76d2957-2bf6-4d8f-90a2-29bf9a927823"
    
    console.print("\n")
    console.print(Panel(
        "[bold cyan]🕷️  FireCrawl Smoke Test[/bold cyan]\n"
        f"[yellow]URL:[/yellow] {job_url}",
        border_style="cyan",
        title="[bold]Job Scraping Test[/bold]"
    ))
    
    try:
        # Scrape the job page
        console.print("[bold]⏳ Scraping job posting...[/bold]")
        result = scrape_job_page(job_url)
        
        console.print("[green]✓ Scrape successful![/green]\n")
        
        # Display metadata
        metadata = result.get("metadata", {})
        
        metadata_table = Table(title="📋 Job Metadata", show_header=True, header_style="bold magenta")
        metadata_table.add_column("Field", style="cyan")
        metadata_table.add_column("Value", style="green")
        
        for key, value in metadata.items():
            if isinstance(value, str) and len(str(value)) > 80:
                value = str(value)[:77] + "..."
            metadata_table.add_row(str(key), str(value))
        
        console.print(metadata_table)
        console.print()
        
        # Display content statistics
        markdown_content = result.get("markdown", "")
        word_count = len(markdown_content.split())
        line_count = len(markdown_content.split("\n"))
        char_count = len(markdown_content)
        
        stats_table = Table(title="📊 Content Statistics", show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        stats_table.add_row("Characters", f"{char_count:,}")
        stats_table.add_row("Words", f"{word_count:,}")
        stats_table.add_row("Lines", f"{line_count:,}")
        
        console.print(stats_table)
        console.print()
        
        # Display first 1000 chars of content
        preview_length = 1000
        preview = markdown_content[:preview_length]
        if len(markdown_content) > preview_length:
            preview += f"\n\n[dim]... ({char_count - preview_length:,} more characters)[/dim]"
        
        console.print(Panel(
            preview,
            title="[bold]📄 Content Preview[/bold]",
            border_style="green",
            expand=False
        ))
        
        # Validate response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "markdown" in result, "Result should contain 'markdown' key"
        assert "metadata" in result, "Result should contain 'metadata' key"
        assert len(markdown_content) > 100, "Markdown content should be substantial"
        
        console.print("\n[bold green]✅ All validations passed![/bold green]\n")
        
        # Return result for assertions
        return result
        
    except CrawlerError as e:
        console.print(f"\n[red]✗ Crawler Error: {e}[/red]")
        console.print(Panel(
            "[yellow]Note:[/yellow] This test requires valid FIRECRAWL_API_KEY in .env file",
            border_style="yellow"
        ))
        pytest.skip(f"FireCrawl API error: {e}")
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error: {e}[/red]")
        pytest.fail(f"Unexpected error during smoke test: {e}")


@pytest.mark.integration
def test_scrape_and_save_output():
    """
    Smoke test: Scrape and save output to JSON file for inspection.
    """
    job_url = "https://jobs.lever.co/mistral/e76d2957-2bf6-4d8f-90a2-29bf9a927823"
    
    console.print("\n")
    console.print(Panel(
        "[bold cyan]💾 FireCrawl Output to JSON[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        result = scrape_job_page(job_url)
        
        # Prepare output structure
        output = {
            "url": job_url,
            "status": "success",
            "metadata": result.get("metadata", {}),
            "content_stats": {
                "characters": len(result.get("markdown", "")),
                "words": len(result.get("markdown", "").split()),
            },
            "content_preview": result.get("markdown", "")[:500]
        }
        
        # Display as formatted JSON
        json_str = json.dumps(output, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        
        console.print(Panel(
            syntax,
            title="[bold]JSON Output[/bold]",
            border_style="green"
        ))
        
        console.print("\n[green]✅ Output generated successfully![/green]\n")
        
    except CrawlerError as e:
        console.print(f"\n[red]✗ Crawler Error: {e}[/red]")
        pytest.skip(f"FireCrawl API error: {e}")


@pytest.mark.integration
def test_scrape_multiple_urls():
    """
    Smoke test: Scrape multiple job URLs and compare results.
    """
    
    urls = [
        "https://jobs.lever.co/mistral/e76d2957-2bf6-4d8f-90a2-29bf9a927823",  # Mistral AI
    ]
    
    console.print("\n")
    console.print(Panel(
        "[bold cyan]🔍 Multi-URL Scraping Test[/bold cyan]",
        border_style="cyan"
    ))
    
    results_table = Table(title="Scraping Results", show_header=True, header_style="bold magenta")
    results_table.add_column("URL", style="cyan", no_wrap=False)
    results_table.add_column("Status", style="yellow")
    results_table.add_column("Words", style="green")
    results_table.add_column("Size (KB)", style="green")
    
    for url in urls:
        try:
            console.print(f"[dim]Scraping: {url}...[/dim]")
            result = scrape_job_page(url)
            markdown = result.get("markdown", "")
            word_count = len(markdown.split())
            size_kb = len(markdown.encode()) / 1024
            
            results_table.add_row(
                url[:50] + "..." if len(url) > 50 else url,
                "[green]✓ Success[/green]",
                f"{word_count:,}",
                f"{size_kb:.2f}"
            )
        except CrawlerError as e:
            results_table.add_row(
                url[:50] + "..." if len(url) > 50 else url,
                f"[red]✗ Error[/red]",
                "-",
                "-"
            )
            console.print(f"[yellow]Skipping due to: {e}[/yellow]")
            pytest.skip(f"FireCrawl API error: {e}")
    
    console.print(results_table)
    console.print()


def test_scraper_config_loaded():
    """Verify that settings are properly loaded."""
    settings = get_settings()
    
    console.print("\n")
    console.print(Panel(
        "[bold cyan]⚙️  Configuration Check[/bold cyan]",
        border_style="cyan"
    ))
    
    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Environment", settings.environments)
    config_table.add_row("Debug Mode", str(settings.debug))
    config_table.add_row("FireCrawl Timeout", f"{settings.firecrawl_timeout}s")
    config_table.add_row("Max Upload Size", f"{settings.max_upload_size_mb}MB")
    config_table.add_row(
        "FireCrawl API Key",
        "[green]✓ Configured[/green]" if settings.firecrawl_api_key else "[red]✗ Missing[/red]"
    )
    
    console.print(config_table)
    console.print()
    
    # Assert critical settings
    assert settings.firecrawl_timeout > 0, "FireCrawl timeout must be positive"
    assert settings.max_upload_size_mb > 0, "Max upload size must be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
