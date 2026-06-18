#!/usr/bin/env python3
"""
Test script for directories spider.
Tests the spider with mock data to verify it works before running on real sites.
"""
import sys
from scrapy.http import HtmlResponse, Request
from app.scrapers.spiders.directories_spider import DirectoriesSpider


def test_spider():
    """Test the spider with mock HTML."""

    # Mock HTML response similar to what we might get from annuaire.tn
    mock_html = """
    <html>
        <body>
            <div class="company-item">
                <h2 class="company-name">Poulina Group Holding</h2>
                <div class="sector">Diversified Industrial</div>
                <div class="city">Tunis</div>
                <div class="phone">+216 71 862 000</div>
                <a class="website" href="https://www.poulina.com.tn">Website</a>
                <p class="description">Leading Tunisian industrial group</p>
            </div>
            <div class="company-item">
                <h2 class="company-name">ENIT</h2>
                <div class="sector">Engineering Education</div>
                <div class="city">Tunis</div>
                <div class="phone">+216 71 872 729</div>
                <a class="website" href="https://www.enit.rnu.tn">Website</a>
            </div>
        </body>
    </html>
    """

    # Create spider instance
    spider = DirectoriesSpider()

    # Create mock response
    url = "https://www.annuaire.tn/cat/industrie.html"
    request = Request(url=url)
    response = HtmlResponse(
        url=url,
        request=request,
        body=mock_html.encode('utf-8'),
        encoding='utf-8'
    )

    # Parse response
    print("Testing DirectoriesSpider.parse()...")
    print("-" * 60)

    results = list(spider.parse(response))

    print(f"\nExtracted {len(results)} items:\n")

    for i, item in enumerate(results, 1):
        if item:
            print(f"Item {i}:")
            for key, value in item.items():
                print(f"  {key}: {value}")
            print()

    if len(results) >= 2:
        print("✅ Spider test PASSED - extracted expected items")
        return True
    else:
        print("❌ Spider test FAILED - did not extract expected items")
        return False


if __name__ == '__main__':
    success = test_spider()
    sys.exit(0 if success else 1)
