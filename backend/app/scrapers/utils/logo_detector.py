"""
Logo and product detection on company websites using Playwright.

Detects:
- SOLIDWORKS logos and mentions
- Simulia, Abaqus logos
- 3DEXPERIENCE platform
- EMWorks, CAMWorks mentions
- Other CAD/simulation software

Creates LeadSignal with signal_type=logo_detected
"""
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright, Page, Browser
import logging

logger = logging.getLogger(__name__)


class LogoDetector:
    """
    Detect SOLIDWORKS and related product logos/mentions on company websites.
    """

    # ABBK Products to detect
    SOLIDWORKS_PRODUCTS = [
        'solidworks', 'solid works',
        'solidworks simulation', 'solidworks flow',
        'solidworks plastics', 'solidworks pdm',
        'solidworks cam', 'camworks',
        'solidworks electrical',
    ]

    SIMULIA_PRODUCTS = [
        'simulia', 'abaqus', 'simula',
    ]

    DASSAULT_PRODUCTS = [
        '3dexperience', '3d experience',
        'catia', 'enovia', 'delmia',
    ]

    EMWORKS_PRODUCTS = [
        'emworks', 'em works',
        'ems', 'hfworks', 'motorwizard',
    ]

    # Competitor products (to detect cracked usage potential)
    COMPETITOR_PRODUCTS = [
        'autodesk', 'inventor', 'fusion 360',
        'autocad', 'revit',
        'creo', 'pro/engineer', 'ptc',
        'nx', 'siemens nx', 'unigraphics',
        'ansys', 'comsol',
        'freecad', 'onshape',
    ]

    # Logo image patterns
    LOGO_PATTERNS = [
        r'solidworks.*\.(?:png|jpg|jpeg|svg|gif)',
        r'sw_logo',
        r'simulia.*\.(?:png|jpg|jpeg|svg|gif)',
        r'abaqus.*\.(?:png|jpg|jpeg|svg|gif)',
        r'3dexperience.*\.(?:png|jpg|jpeg|svg|gif)',
        r'dassault.*\.(?:png|jpg|jpeg|svg|gif)',
    ]

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize logo detector.

        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout

    async def detect_on_website(self, url: str) -> Dict[str, any]:
        """
        Detect logos and product mentions on a website.

        Args:
            url: Website URL to check

        Returns:
            Dict with detection results:
            {
                'url': str,
                'solidworks_detected': bool,
                'simulia_detected': bool,
                'products_found': List[str],
                'logo_urls': List[str],
                'text_mentions': List[str],
                'competitor_products': List[str],
                'screenshot_path': Optional[str],
                'error': Optional[str]
            }
        """
        result = {
            'url': url,
            'solidworks_detected': False,
            'simulia_detected': False,
            '3dexperience_detected': False,
            'emworks_detected': False,
            'products_found': [],
            'logo_urls': [],
            'text_mentions': [],
            'competitor_products': [],
            'screenshot_path': None,
            'error': None,
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()

                try:
                    # Navigate to website
                    await page.goto(url, timeout=self.timeout, wait_until='networkidle')

                    # Extract page content
                    page_text = await page.inner_text('body')
                    page_html = await page.content()

                    # Detect SOLIDWORKS
                    sw_results = self._detect_solidworks(page_text, page_html)
                    if sw_results:
                        result['solidworks_detected'] = True
                        result['products_found'].extend(sw_results['products'])
                        result['logo_urls'].extend(sw_results['logos'])
                        result['text_mentions'].extend(sw_results['mentions'])

                    # Detect Simulia/Abaqus
                    simulia_results = self._detect_simulia(page_text, page_html)
                    if simulia_results:
                        result['simulia_detected'] = True
                        result['products_found'].extend(simulia_results['products'])
                        result['logo_urls'].extend(simulia_results['logos'])
                        result['text_mentions'].extend(simulia_results['mentions'])

                    # Detect 3DEXPERIENCE
                    exp_results = self._detect_3dexperience(page_text, page_html)
                    if exp_results:
                        result['3dexperience_detected'] = True
                        result['products_found'].extend(exp_results['products'])
                        result['logo_urls'].extend(exp_results['logos'])
                        result['text_mentions'].extend(exp_results['mentions'])

                    # Detect EMWorks
                    em_results = self._detect_emworks(page_text, page_html)
                    if em_results:
                        result['emworks_detected'] = True
                        result['products_found'].extend(em_results['products'])
                        result['text_mentions'].extend(em_results['mentions'])

                    # Detect competitor products (indicates potential cracked SW usage)
                    competitors = self._detect_competitors(page_text)
                    result['competitor_products'] = competitors

                    # Get all images that might be logos
                    logo_images = await self._extract_logo_images(page)
                    result['logo_urls'].extend(logo_images)

                    # Deduplicate
                    result['products_found'] = list(set(result['products_found']))
                    result['logo_urls'] = list(set(result['logo_urls']))
                    result['text_mentions'] = list(set(result['text_mentions']))
                    result['competitor_products'] = list(set(result['competitor_products']))

                    logger.info(f"✅ Detected on {url}: {len(result['products_found'])} products")

                except Exception as e:
                    result['error'] = str(e)
                    logger.error(f"Error detecting logos on {url}: {e}")

                finally:
                    await browser.close()

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Browser error for {url}: {e}")

        return result

    def _detect_solidworks(self, text: str, html: str) -> Optional[Dict]:
        """Detect SOLIDWORKS products."""
        text_lower = text.lower()
        html_lower = html.lower()

        products = []
        logos = []
        mentions = []

        for product in self.SOLIDWORKS_PRODUCTS:
            if product in text_lower:
                products.append(product.title())
                # Find context around mention
                context = self._extract_context(text, product)
                if context:
                    mentions.append(context)

        # Check for logo images
        for pattern in self.LOGO_PATTERNS:
            matches = re.findall(pattern, html_lower, re.IGNORECASE)
            logos.extend(matches)

        if products or logos:
            return {
                'products': products,
                'logos': logos,
                'mentions': mentions,
            }

        return None

    def _detect_simulia(self, text: str, html: str) -> Optional[Dict]:
        """Detect Simulia/Abaqus products."""
        text_lower = text.lower()
        products = []
        logos = []
        mentions = []

        for product in self.SIMULIA_PRODUCTS:
            if product in text_lower:
                products.append(product.title())
                context = self._extract_context(text, product)
                if context:
                    mentions.append(context)

        if products:
            return {
                'products': products,
                'logos': logos,
                'mentions': mentions,
            }

        return None

    def _detect_3dexperience(self, text: str, html: str) -> Optional[Dict]:
        """Detect 3DEXPERIENCE platform."""
        text_lower = text.lower()
        products = []
        logos = []
        mentions = []

        for product in self.DASSAULT_PRODUCTS:
            if product in text_lower:
                products.append(product.upper())
                context = self._extract_context(text, product)
                if context:
                    mentions.append(context)

        if products:
            return {
                'products': products,
                'logos': logos,
                'mentions': mentions,
            }

        return None

    def _detect_emworks(self, text: str, html: str) -> Optional[Dict]:
        """Detect EMWorks products."""
        text_lower = text.lower()
        products = []
        mentions = []

        for product in self.EMWORKS_PRODUCTS:
            if product in text_lower:
                products.append(product.upper())
                context = self._extract_context(text, product)
                if context:
                    mentions.append(context)

        if products:
            return {
                'products': products,
                'logos': [],
                'mentions': mentions,
            }

        return None

    def _detect_competitors(self, text: str) -> List[str]:
        """Detect competitor CAD/simulation products."""
        text_lower = text.lower()
        found = []

        for product in self.COMPETITOR_PRODUCTS:
            if product in text_lower:
                found.append(product.title())

        return found

    def _extract_context(self, text: str, keyword: str, context_size: int = 100) -> Optional[str]:
        """Extract context around a keyword mention."""
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        index = text_lower.find(keyword_lower)
        if index == -1:
            return None

        start = max(0, index - context_size)
        end = min(len(text), index + len(keyword) + context_size)

        context = text[start:end].strip()
        return context if len(context) > 10 else None

    async def _extract_logo_images(self, page: Page) -> List[str]:
        """Extract image URLs that might be logos."""
        logo_urls = []

        try:
            # Get all images
            images = await page.query_selector_all('img')

            for img in images:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                class_name = await img.get_attribute('class')

                if not src:
                    continue

                # Check if image might be a product logo
                indicators = [src, alt or '', class_name or '']
                combined = ' '.join(indicators).lower()

                if any(keyword in combined for keyword in ['solidworks', 'simulia', 'abaqus', '3dexperience', 'logo', 'partner']):
                    logo_urls.append(src)

        except Exception as e:
            logger.warning(f"Error extracting logo images: {e}")

        return logo_urls[:10]  # Limit to 10 logos


async def detect_logos_batch(urls: List[str], headless: bool = True) -> List[Dict]:
    """
    Detect logos on multiple URLs in batch.

    Args:
        urls: List of URLs to check
        headless: Run in headless mode

    Returns:
        List of detection results
    """
    detector = LogoDetector(headless=headless)
    results = []

    for url in urls:
        result = await detector.detect_on_website(url)
        results.append(result)

        # Small delay between requests
        await asyncio.sleep(2)

    return results
