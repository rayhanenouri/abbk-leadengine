"""
Detection utilities for lead enrichment.

Functions to detect:
- is_multinational: company is part of international group
- is_exporter: company exports internationally
- under_audit: company under ISO/international audit

These are ABBK's highest converting leads.
"""
import re
from typing import Dict, Any, Tuple


class LeadDetector:
    """
    Detect high-value signals from scraped data and text.
    """

    # Multinational indicators
    MULTINATIONAL_KEYWORDS = [
        # English
        'multinational', 'international group', 'global group', 'worldwide',
        'subsidiary', 'filiale', 'branch', 'headquarters',
        'parent company', 'holding', 'corporation',

        # French
        'groupe international', 'groupe mondial', 'multinationale',
        'filiale de', 'succursale', 'siège social',
        'société mère', 'groupe holding',

        # Specific patterns
        'part of', 'owned by', 'acquired by',
        'membre de', 'appartient à',
    ]

    # Known multinational groups with presence in Tunisia
    KNOWN_MULTINATIONALS = [
        'stmicroelectronics', 'leoni', 'valeo', 'lear', 'delphi',
        'faurecia', 'yazaki', 'continental', 'schneider electric',
        'saint gobain', 'lafarge', 'holcim', 'danone', 'nestlé',
        'poulina', 'loukil', 'driss', 'mabrouk', 'elloumi',
        'telnet', 'orange', 'ooredoo', 'hexabyte',
    ]

    # Export indicators
    EXPORT_KEYWORDS = [
        # Direct export terms
        'export', 'exporter', 'exportation', 'exportateur',
        'international market', 'marché international',
        'overseas', 'abroad', 'étranger',

        # Export destinations/activities
        'contrat international', 'international contract',
        'partenaire international', 'international partner',
        'client international', 'international client',
        'vente à l\'étranger', 'sales abroad',

        # Geographic indicators
        'europe', 'africa', 'afrique', 'middle east',
        'moyen orient', 'maghreb', 'asia', 'asie',
    ]

    # Countries that indicate export activity
    EXPORT_COUNTRIES = [
        'france', 'germany', 'allemagne', 'italy', 'italie',
        'spain', 'espagne', 'uk', 'united kingdom', 'royaume uni',
        'algeria', 'algérie', 'morocco', 'maroc', 'libya', 'libye',
        'egypt', 'égypte', 'saudi', 'arabie', 'dubai', 'emirats',
    ]

    # Audit/Certification indicators
    AUDIT_KEYWORDS = [
        # ISO standards
        'iso 9001', 'iso 14001', 'iso 45001', 'iso 27001',
        'iso 13485', 'iso 22000', 'iso 50001',
        'iso certification', 'iso certified', 'certifié iso',
        'certification iso',

        # Other certifications
        'ce marking', 'ce mark', 'marquage ce',
        'fda approved', 'fda certification',
        'gmp', 'good manufacturing practice',
        'haccp', 'brc', 'ifs',

        # Audit terms
        'audit', 'audited', 'audité', 'audit international',
        'international audit', 'compliance', 'conformité',
        'accréditation', 'accreditation',
        'qualité certifiée', 'certified quality',

        # Quality management
        'quality management system', 'système de management',
        'norme internationale', 'international standard',
        'certification process', 'processus de certification',
    ]

    # Compliance requirements
    COMPLIANCE_KEYWORDS = [
        'compliance requirement', 'exigence de conformité',
        'regulatory compliance', 'conformité réglementaire',
        'quality assurance', 'assurance qualité',
        'third party audit', 'audit tiers',
        'external audit', 'audit externe',
    ]

    @staticmethod
    def detect_multinational(
        company_name: str,
        scraped_data: Dict[str, Any],
        website_text: str = ""
    ) -> Tuple[bool, str]:
        """
        Detect if company is multinational.

        Returns: (is_multinational: bool, reason: str)
        """
        reasons = []

        # Convert to lowercase for matching
        name_lower = company_name.lower()
        all_text = f"{company_name} {website_text} {str(scraped_data)}".lower()

        # Check 1: Known multinational names
        for multinational in LeadDetector.KNOWN_MULTINATIONALS:
            if multinational in name_lower:
                reasons.append(f"Known multinational: {multinational}")
                return True, "; ".join(reasons)

        # Check 2: Multinational keywords in text
        for keyword in LeadDetector.MULTINATIONAL_KEYWORDS:
            if keyword in all_text:
                reasons.append(f"Multinational indicator: {keyword}")

        # Check 3: Multiple country mentions (indicates international presence)
        countries_mentioned = sum(
            1 for country in LeadDetector.EXPORT_COUNTRIES
            if country in all_text
        )
        if countries_mentioned >= 3:
            reasons.append(f"{countries_mentioned} countries mentioned - international presence")

        # Check 4: Scraped data indicators
        if scraped_data:
            # Check LinkedIn data
            linkedin_data = scraped_data.get('linkedin', {})
            if isinstance(linkedin_data, dict):
                specialties = str(linkedin_data.get('specialties', '')).lower()
                if any(kw in specialties for kw in ['international', 'global', 'worldwide']):
                    reasons.append("LinkedIn: international specialties")

            # Check news mentions
            news_items = scraped_data.get('news', [])
            if isinstance(news_items, list):
                for news in news_items[:5]:  # Check recent news
                    if any(kw in str(news).lower() for kw in LeadDetector.MULTINATIONAL_KEYWORDS):
                        reasons.append("News: multinational mention")
                        break

        is_multinational = len(reasons) >= 2  # Need at least 2 indicators
        return is_multinational, "; ".join(reasons) if reasons else "No multinational indicators"

    @staticmethod
    def detect_exporter(
        company_name: str,
        scraped_data: Dict[str, Any],
        sector: str = "",
        website_text: str = ""
    ) -> Tuple[bool, str]:
        """
        Detect if company exports internationally.

        Returns: (is_exporter: bool, reason: str)
        """
        reasons = []

        all_text = f"{company_name} {sector} {website_text} {str(scraped_data)}".lower()

        # Check 1: Direct export keywords
        export_mentions = sum(1 for kw in LeadDetector.EXPORT_KEYWORDS if kw in all_text)
        if export_mentions >= 2:
            reasons.append(f"{export_mentions} export indicators found")

        # Check 2: Foreign country mentions
        countries_mentioned = [
            country for country in LeadDetector.EXPORT_COUNTRIES
            if country in all_text
        ]
        if len(countries_mentioned) >= 2:
            reasons.append(f"Exports to: {', '.join(countries_mentioned[:3])}")

        # Check 3: Export-oriented sectors
        export_sectors = [
            'textile', 'automotive', 'electronics', 'électronique',
            'manufacturing', 'fabrication', 'agro', 'pharmaceutical',
            'pharmaceutique', 'cosmetic', 'cosmétique', 'machinery',
        ]
        if any(s in all_text for s in export_sectors):
            if any(kw in all_text for kw in ['export', 'international', 'étranger']):
                reasons.append(f"Export-oriented sector: {sector}")

        # Check 4: Scraped data indicators
        if scraped_data:
            # Check news for export contracts
            news_items = scraped_data.get('news', [])
            if isinstance(news_items, list):
                for news in news_items:
                    news_text = str(news).lower()
                    if 'export' in news_text or 'contrat international' in news_text:
                        reasons.append("News: export contract mentioned")
                        break

            # Check LinkedIn data
            linkedin_data = scraped_data.get('linkedin', {})
            if isinstance(linkedin_data, dict):
                description = str(linkedin_data.get('description', '')).lower()
                if 'export' in description or 'international market' in description:
                    reasons.append("LinkedIn: export activity mentioned")

        is_exporter = len(reasons) >= 2  # Need at least 2 indicators
        return is_exporter, "; ".join(reasons) if reasons else "No export indicators"

    @staticmethod
    def detect_audit_pressure(
        company_name: str,
        scraped_data: Dict[str, Any],
        website_text: str = ""
    ) -> Tuple[bool, str]:
        """
        Detect if company is under audit/certification pressure.

        These companies CANNOT use cracked software - highest conversion.

        Returns: (under_audit: bool, reason: str)
        """
        reasons = []

        all_text = f"{company_name} {website_text} {str(scraped_data)}".lower()

        # Check 1: ISO certifications
        iso_standards = ['iso 9001', 'iso 14001', 'iso 45001', 'iso 27001', 'iso 13485']
        for iso in iso_standards:
            if iso in all_text:
                reasons.append(f"Has {iso.upper()} certification")

        # Check 2: Audit keywords
        audit_mentions = sum(1 for kw in LeadDetector.AUDIT_KEYWORDS if kw in all_text)
        if audit_mentions >= 3:
            reasons.append(f"{audit_mentions} audit/certification indicators")

        # Check 3: Compliance keywords
        compliance_mentions = sum(1 for kw in LeadDetector.COMPLIANCE_KEYWORDS if kw in all_text)
        if compliance_mentions >= 2:
            reasons.append(f"{compliance_mentions} compliance indicators")

        # Check 4: Quality certifications in scraped data
        if scraped_data:
            # Check website content
            about = scraped_data.get('about', '')
            if isinstance(about, str) and any(kw in about.lower() for kw in LeadDetector.AUDIT_KEYWORDS):
                reasons.append("Website: certification mentioned")

            # Check news for certification announcements
            news_items = scraped_data.get('news', [])
            if isinstance(news_items, list):
                for news in news_items:
                    news_text = str(news).lower()
                    if any(kw in news_text for kw in ['iso', 'certification', 'audit', 'certifié']):
                        reasons.append("News: certification activity")
                        break

        # Check 5: Regulated industries (pharmaceuticals, medical, aerospace)
        regulated_sectors = [
            'pharmaceutique', 'pharmaceutical', 'medical', 'médical',
            'aerospace', 'aéronautique', 'automotive tier 1',
            'food processing', 'agro-alimentaire',
        ]
        if any(s in all_text for s in regulated_sectors):
            reasons.append("Regulated industry - requires compliance")

        under_audit = len(reasons) >= 2  # Need at least 2 indicators
        return under_audit, "; ".join(reasons) if reasons else "No audit indicators"

    @staticmethod
    def enrich_lead(
        company_name: str,
        scraped_data: Dict[str, Any],
        sector: str = "",
        website_text: str = ""
    ) -> Dict[str, Any]:
        """
        Enrich lead with all detection flags.

        Returns dict with:
        - is_multinational: bool
        - multinational_reason: str
        - is_exporter: bool
        - exporter_reason: str
        - under_audit: bool
        - audit_reason: str
        """
        is_multi, multi_reason = LeadDetector.detect_multinational(
            company_name, scraped_data, website_text
        )

        is_export, export_reason = LeadDetector.detect_exporter(
            company_name, scraped_data, sector, website_text
        )

        is_audit, audit_reason = LeadDetector.detect_audit_pressure(
            company_name, scraped_data, website_text
        )

        return {
            'is_multinational': is_multi,
            'multinational_reason': multi_reason,
            'is_exporter': is_export,
            'exporter_reason': export_reason,
            'under_audit': is_audit,
            'audit_reason': audit_reason,
        }
