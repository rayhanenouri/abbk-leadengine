"""
Test logo detection on sample websites.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.utils.logo_detector import LogoDetector


async def test_logo_detection():
    """Test logo detector on known websites."""
    print("=" * 70)
    print("Testing Logo Detection")
    print("=" * 70)

    # Test URLs (ABBK website and partners)
    test_urls = [
        "https://www.abbk-tn.com",  # ABBK itself
        "https://www.solidworks.com",  # SOLIDWORKS official
        "https://www.3ds.com",  # Dassault Systemes
    ]

    detector = LogoDetector(headless=True, timeout=30000)

    for url in test_urls:
        print(f"\n📍 Checking: {url}")
        print("-" * 70)

        result = await detector.detect_on_website(url)

        if result['error']:
            print(f"❌ Error: {result['error']}")
            continue

        print(f"✅ Detection complete:")
        print(f"   SOLIDWORKS: {result['solidworks_detected']}")
        print(f"   Simulia: {result['simulia_detected']}")
        print(f"   3DEXPERIENCE: {result['3dexperience_detected']}")
        print(f"   EMWorks: {result['emworks_detected']}")
        print(f"   Products found: {result['products_found']}")
        print(f"   Logo URLs: {len(result['logo_urls'])}")
        print(f"   Text mentions: {len(result['text_mentions'])}")
        if result['competitor_products']:
            print(f"   ⚠️  Competitors: {result['competitor_products']}")

        if result['text_mentions']:
            print(f"\n   Sample mentions:")
            for mention in result['text_mentions'][:2]:
                print(f"   - {mention[:100]}...")

    print("\n" + "=" * 70)
    print("Test complete")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_logo_detection())
