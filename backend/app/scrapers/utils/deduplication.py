"""
Data deduplication and multi-source merging utilities.

Handles:
- Duplicate company detection (fuzzy matching)
- Multi-source data merging
- Company name normalization
- Website URL canonicalization
"""
import re
from typing import List, Tuple, Optional, Dict
from difflib import SequenceMatcher
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class DeduplicationEngine:
    """
    Detect and merge duplicate companies from multiple sources.
    """

    # Common company suffixes to ignore during matching
    COMPANY_SUFFIXES = [
        'sa', 'sarl', 'suarl', 'surl',
        'holding', 'group', 'groupe',
        'corporation', 'corp',
        'international', 'tunisia', 'tunisie',
        'industries', 'services',
        'limited', 'ltd', 'llc',
    ]

    # Company type prefixes to normalize
    COMPANY_PREFIXES = [
        'société', 'societe',
        'entreprise',
        'ste',
    ]

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """
        Normalize company name for matching.

        Removes:
        - Common suffixes (SA, SARL, etc.)
        - Special characters
        - Extra whitespace
        - Accents (optional)

        Args:
            name: Original company name

        Returns:
            Normalized name for matching
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower().strip()

        # Remove common punctuation
        normalized = re.sub(r'[.,;:\-_()"\']', ' ', normalized)

        # Remove company suffixes
        for suffix in DeduplicationEngine.COMPANY_SUFFIXES:
            # Remove as whole word
            normalized = re.sub(rf'\b{suffix}\b', '', normalized, flags=re.IGNORECASE)

        # Remove company prefixes
        for prefix in DeduplicationEngine.COMPANY_PREFIXES:
            # Remove from start
            normalized = re.sub(rf'^{prefix}\s+', '', normalized, flags=re.IGNORECASE)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    @staticmethod
    def normalize_website(url: str) -> Optional[str]:
        """
        Normalize website URL for comparison.

        Converts:
        - http://www.example.com → example.com
        - https://example.com/path → example.com
        - www.example.com → example.com

        Args:
            url: Website URL

        Returns:
            Normalized domain name
        """
        if not url:
            return None

        try:
            # Parse URL
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Remove www.
            if domain.startswith('www.'):
                domain = domain[4:]

            return domain if domain else None

        except Exception as e:
            logger.warning(f"Error normalizing URL {url}: {e}")
            return None

    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """
        Calculate similarity between two company names.

        Uses SequenceMatcher for fuzzy string matching.

        Args:
            name1: First company name
            name2: Second company name

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not name1 or not name2:
            return 0.0

        # Normalize both names
        norm1 = DeduplicationEngine.normalize_company_name(name1)
        norm2 = DeduplicationEngine.normalize_company_name(name2)

        if not norm1 or not norm2:
            return 0.0

        # Calculate sequence similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        return similarity

    @staticmethod
    def are_duplicates(
        name1: str,
        name2: str,
        website1: Optional[str] = None,
        website2: Optional[str] = None,
        threshold: float = 0.85
    ) -> Tuple[bool, float, str]:
        """
        Determine if two companies are duplicates.

        Matching logic:
        1. Exact website match → 100% duplicate
        2. Name similarity >= threshold → likely duplicate
        3. Partial website + high name similarity → duplicate

        Args:
            name1, name2: Company names
            website1, website2: Optional websites
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            (is_duplicate: bool, confidence: float, reason: str)
        """
        # Check website match (strongest signal)
        if website1 and website2:
            norm_web1 = DeduplicationEngine.normalize_website(website1)
            norm_web2 = DeduplicationEngine.normalize_website(website2)

            if norm_web1 and norm_web2 and norm_web1 == norm_web2:
                return (True, 1.0, f"Exact website match: {norm_web1}")

        # Check name similarity
        name_similarity = DeduplicationEngine.calculate_similarity(name1, name2)

        if name_similarity >= threshold:
            return (True, name_similarity, f"High name similarity: {name_similarity:.2f}")

        # Check if names are very similar and have partial website match
        if name_similarity >= 0.7 and website1 and website2:
            norm_web1 = DeduplicationEngine.normalize_website(website1)
            norm_web2 = DeduplicationEngine.normalize_website(website2)

            if norm_web1 and norm_web2:
                # Check if domains are similar (e.g., company.tn vs company.com.tn)
                domain1_parts = norm_web1.split('.')
                domain2_parts = norm_web2.split('.')

                if domain1_parts[0] == domain2_parts[0]:  # Same base domain
                    return (True, 0.9, f"Same base domain + similar name: {domain1_parts[0]}")

        return (False, name_similarity, "Not a duplicate")

    @staticmethod
    def merge_lead_data(
        primary: Dict,
        secondary: Dict,
        conflict_resolution: str = "primary"
    ) -> Dict:
        """
        Merge data from duplicate leads.

        Strategy:
        - Primary lead keeps its ID and main fields
        - Missing fields filled from secondary
        - scraped_data merged (all sources preserved)
        - Signals from both leads combined

        Args:
            primary: Primary lead data (dict)
            secondary: Secondary lead data (dict)
            conflict_resolution: How to resolve conflicts ("primary", "secondary", "newest")

        Returns:
            Merged lead data
        """
        merged = primary.copy()

        # Fields to merge (prefer non-None values)
        merge_fields = [
            'website', 'linkedin_url', 'country', 'city', 'sector',
            'employee_count', 'is_multinational', 'is_exporter', 'under_audit'
        ]

        for field in merge_fields:
            primary_val = primary.get(field)
            secondary_val = secondary.get(field)

            if primary_val is None and secondary_val is not None:
                merged[field] = secondary_val
            elif conflict_resolution == "secondary" and secondary_val is not None:
                merged[field] = secondary_val

        # Merge scraped_data (combine all sources)
        primary_scraped = primary.get('scraped_data', {}) or {}
        secondary_scraped = secondary.get('scraped_data', {}) or {}

        merged_scraped = {}

        # Add all sources from primary
        for source_key, source_data in primary_scraped.items():
            merged_scraped[source_key] = source_data

        # Add sources from secondary (with conflict handling)
        for source_key, source_data in secondary_scraped.items():
            if source_key not in merged_scraped:
                merged_scraped[source_key] = source_data
            else:
                # Both have same source - merge or keep newest
                if isinstance(source_data, dict) and isinstance(merged_scraped[source_key], dict):
                    merged_scraped[source_key].update(source_data)

        merged['scraped_data'] = merged_scraped

        # Add merge metadata
        merged['scraped_data']['_merge_info'] = {
            'merged_from_lead_id': secondary.get('id'),
            'merged_at': 'timestamp',  # Will be set by caller
            'merge_reason': 'duplicate_detected',
        }

        return merged

    @staticmethod
    def find_duplicates_in_list(
        leads: List[Dict],
        threshold: float = 0.85
    ) -> List[Tuple[int, int, float, str]]:
        """
        Find all duplicate pairs in a list of leads.

        Args:
            leads: List of lead dicts (must have 'company_name' and optionally 'website')
            threshold: Similarity threshold

        Returns:
            List of tuples: (index1, index2, confidence, reason)
        """
        duplicates = []

        for i in range(len(leads)):
            for j in range(i + 1, len(leads)):
                lead1 = leads[i]
                lead2 = leads[j]

                is_dup, confidence, reason = DeduplicationEngine.are_duplicates(
                    name1=lead1.get('company_name', ''),
                    name2=lead2.get('company_name', ''),
                    website1=lead1.get('website'),
                    website2=lead2.get('website'),
                    threshold=threshold
                )

                if is_dup:
                    duplicates.append((i, j, confidence, reason))

        return duplicates


def deduplicate_companies(
    companies: List[Dict],
    threshold: float = 0.85,
    auto_merge: bool = False
) -> Tuple[List[Dict], List[Dict]]:
    """
    Deduplicate a list of companies.

    Args:
        companies: List of company dicts
        threshold: Similarity threshold for duplicate detection
        auto_merge: If True, automatically merge duplicates

    Returns:
        (unique_companies, duplicates_found)
    """
    engine = DeduplicationEngine()

    # Find all duplicates
    duplicate_pairs = engine.find_duplicates_in_list(companies, threshold)

    if not duplicate_pairs:
        return companies, []

    # Build duplicate groups
    duplicate_groups = {}
    for idx1, idx2, confidence, reason in duplicate_pairs:
        if idx1 not in duplicate_groups:
            duplicate_groups[idx1] = []
        duplicate_groups[idx1].append((idx2, confidence, reason))

    # Merge or mark duplicates
    if auto_merge:
        # Keep only unique companies (merge duplicates into first occurrence)
        seen = set()
        unique = []

        for i, company in enumerate(companies):
            if i in seen:
                continue

            # Check if this is a primary in any duplicate group
            if i in duplicate_groups:
                # Merge all duplicates into this one
                merged = company.copy()
                for dup_idx, conf, reason in duplicate_groups[i]:
                    if dup_idx not in seen:
                        merged = engine.merge_lead_data(merged, companies[dup_idx])
                        seen.add(dup_idx)
                        logger.info(f"Merged duplicate: {company.get('company_name')} + {companies[dup_idx].get('company_name')} ({reason})")

                unique.append(merged)
            else:
                unique.append(company)

            seen.add(i)

        duplicates_info = [
            {
                'primary': companies[idx1]['company_name'],
                'duplicate': companies[idx2]['company_name'],
                'confidence': conf,
                'reason': reason
            }
            for idx1, idx2, conf, reason in duplicate_pairs
        ]

        return unique, duplicates_info

    else:
        # Just return info about duplicates without merging
        duplicates_info = [
            {
                'primary_index': idx1,
                'duplicate_index': idx2,
                'primary_name': companies[idx1]['company_name'],
                'duplicate_name': companies[idx2]['company_name'],
                'confidence': conf,
                'reason': reason
            }
            for idx1, idx2, conf, reason in duplicate_pairs
        ]

        return companies, duplicates_info
