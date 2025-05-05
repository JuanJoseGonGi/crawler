import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str
    max_depth: int = 2 # Default depth if not provided

async def run_crawler(url: str, max_depth: int):
    """Runs the web crawler with the given URL and max depth."""
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=max_depth,
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True  # Keep verbose for now, can be configured later
    )

    results_summary = []
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url, config=config)

        results_summary.append(f"Crawled {len(results)} pages in total for {url}")

        # Access individual results
        for result in results[:3]:  # Show first 3 results details
            results_summary.append(f"URL: {result.url}, Depth: {result.metadata.get('depth', 0)}")

    return results_summary

@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    """API endpoint to trigger a crawl."""
    print(f"Received crawl request for URL: {request.url} with max depth: {request.max_depth}")
    results = await run_crawler(request.url, request.max_depth)
    return {"message": "Crawl finished.", "results_summary": results}


if __name__ == "__main__":
    # Removed asyncio.run(main()) as it's now handled by FastAPI/uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)