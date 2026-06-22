"""
Claude API Signal Extraction Service.
Uses Claude Sonnet 4.5 to extract boolean signals from raw scraped text.
Dramatically improves score accuracy beyond simple keyword matching.
"""

import json
import hashlib
from typing import Dict, Optional, Tuple
from anthropic import Anthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.models import Lead


class ClaudeSignalExtractor:
    """
    Extracts boolean signals from lead scraped data using Claude API.
    Caches all responses to avoid redundant API calls.
    """

    def __init__(self):
        """Initialize Anthropic client."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5"

    def _get_text_hash(self, text: str) -> str:
        """Generate hash of input text for caching."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _build_extraction_prompt(self, company_name: str, scraped_data: Dict) -> str:
        """
        Build prompt for Claude API to extract signals.

        Args:
            company_name: Name of the company
            scraped_data: Raw scraped data from all sources

        Returns:
            Formatted prompt string
        """
        # Extract relevant text from scraped_data
        text_parts = []

        if isinstance(scraped_data, dict):
            for key, value in scraped_data.items():
                if isinstance(value, (str, list, dict)):
                    text_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False)[:1000]}")
        elif isinstance(scraped_data, str):
            text_parts.append(scraped_data[:2000])

        combined_text = "\n".join(text_parts)[:3000]  # Limit to 3000 chars

        prompt = f"""You are analyzing data for "{company_name}", a Tunisian company, to detect buying signals for SOLIDWORKS CAD software and engineering training programs.

SCRAPED DATA:
{combined_text}

Extract the following boolean signals (respond with true/false for each):

1. has_mechanical_engineer: Does the company employ mechanical engineers, conception engineers, or CAD designers?
2. has_cad_designer: Does the company have CAD/DAO designers or bureau d'études engineers?
3. has_simulation_engineer: Does the company have simulation, FEA, CFD, or calcul engineers?
4. is_multinational: Is this a multinational company, international group, or has international parent company?
5. is_exporter: Does the company export products internationally or serve foreign clients?
6. under_audit: Is the company under ISO certification, international audit, or compliance review?
7. uses_solidworks_logo: Is SOLIDWORKS, Simulia, Abaqus, or 3DEXPERIENCE mentioned or logo detected?
8. did_technical_training: Did the company recently send engineers to technical or CAD training?
9. attended_engineering_event: Did the company attend engineering salons, SOLIDWORKS events, or industry conferences?
10. has_new_engineers: Is the company currently hiring or recently hired mechanical/CAD engineers?
11. recent_funding: Did the company receive investment, funding, or international financing recently?
12. tender_detected: Did the company win or bid on engineering tenders or public contracts?
13. cracked_risk: Does the company likely use cracked/pirated SOLIDWORKS (has engineers but no license signals)?

Respond ONLY with valid JSON in this exact format:
{{
  "has_mechanical_engineer": true/false,
  "has_cad_designer": true/false,
  "has_simulation_engineer": true/false,
  "is_multinational": true/false,
  "is_exporter": true/false,
  "under_audit": true/false,
  "uses_solidworks_logo": true/false,
  "did_technical_training": true/false,
  "attended_engineering_event": true/false,
  "has_new_engineers": true/false,
  "recent_funding": true/false,
  "tender_detected": true/false,
  "cracked_risk": true/false,
  "confidence": "high/medium/low",
  "reasoning": "Brief 1-2 sentence explanation of key findings"
}}

Be strict: only return true if there is clear evidence in the data. Default to false if uncertain."""

        return prompt

    async def extract_signals(
        self,
        db: AsyncSession,
        lead: Lead
    ) -> Tuple[Dict, bool]:
        """
        Extract signals from lead's scraped data using Claude API.

        Args:
            db: Database session
            lead: Lead object with scraped_data

        Returns:
            Tuple of (extracted_signals dict, was_cached bool)
        """
        # Check if scraped_data exists
        if not lead.scraped_data:
            return {}, False

        # Check cache first
        if isinstance(lead.scraped_data, dict) and "claude_signals" in lead.scraped_data:
            return lead.scraped_data["claude_signals"], True

        # Build prompt
        prompt = self._build_extraction_prompt(lead.company_name, lead.scraped_data)

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0,  # Deterministic for consistent results
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Try to parse JSON (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            signals = json.loads(response_text)

            # Validate response structure
            required_keys = [
                "has_mechanical_engineer", "has_cad_designer", "has_simulation_engineer",
                "is_multinational", "is_exporter", "under_audit", "uses_solidworks_logo",
                "did_technical_training", "attended_engineering_event", "has_new_engineers",
                "recent_funding", "tender_detected", "cracked_risk"
            ]

            for key in required_keys:
                if key not in signals:
                    signals[key] = False

            # Cache response in scraped_data
            if not isinstance(lead.scraped_data, dict):
                lead.scraped_data = {}

            lead.scraped_data["claude_signals"] = signals
            lead.scraped_data["claude_model"] = self.model
            lead.scraped_data["claude_extracted_at"] = response.id  # Use response ID as timestamp marker

            # Mark for DB update
            from sqlalchemy.orm import attributes
            attributes.flag_modified(lead, "scraped_data")

            await db.commit()

            return signals, False

        except json.JSONDecodeError as e:
            print(f"Failed to parse Claude response for {lead.company_name}: {e}")
            print(f"Response was: {response_text[:200]}")
            return {}, False
        except Exception as e:
            print(f"Claude API error for {lead.company_name}: {e}")
            return {}, False

    async def extract_signals_batch(
        self,
        db: AsyncSession,
        lead_ids: list[int],
        skip_cached: bool = True
    ) -> Dict[int, Dict]:
        """
        Extract signals for multiple leads in batch.

        Args:
            db: Database session
            lead_ids: List of lead IDs to process
            skip_cached: Skip leads that already have cached signals

        Returns:
            Dict mapping lead_id to extracted signals
        """
        results = {}

        # Fetch leads
        query = select(Lead).where(Lead.id.in_(lead_ids))
        result = await db.execute(query)
        leads = result.scalars().all()

        for lead in leads:
            # Skip if cached and skip_cached is True
            if skip_cached and isinstance(lead.scraped_data, dict):
                if "claude_signals" in lead.scraped_data:
                    results[lead.id] = lead.scraped_data["claude_signals"]
                    continue

            # Extract signals
            signals, was_cached = await self.extract_signals(db, lead)
            results[lead.id] = signals

        return results

    async def reextract_all(self, db: AsyncSession, force: bool = False) -> Dict:
        """
        Re-extract signals for all leads with scraped_data.

        Args:
            db: Database session
            force: If True, re-extract even if cached

        Returns:
            Dict with statistics
        """
        # Get all leads with scraped_data
        query = select(Lead).where(Lead.scraped_data.isnot(None))
        result = await db.execute(query)
        leads = result.scalars().all()

        stats = {
            "total_leads": len(leads),
            "processed": 0,
            "cached": 0,
            "extracted": 0,
            "failed": 0
        }

        for lead in leads:
            # Skip cached unless force=True
            if not force and isinstance(lead.scraped_data, dict):
                if "claude_signals" in lead.scraped_data:
                    stats["cached"] += 1
                    continue

            signals, was_cached = await self.extract_signals(db, lead)

            if signals:
                if was_cached:
                    stats["cached"] += 1
                else:
                    stats["extracted"] += 1
            else:
                stats["failed"] += 1

            stats["processed"] += 1

        return stats


async def get_claude_signals(db: AsyncSession, lead_id: int) -> Optional[Dict]:
    """
    Get Claude-extracted signals for a lead.

    Args:
        db: Database session
        lead_id: Lead ID

    Returns:
        Dict of signals or None if not extracted
    """
    query = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(query)
    lead = result.scalar_one_or_none()

    if not lead or not isinstance(lead.scraped_data, dict):
        return None

    return lead.scraped_data.get("claude_signals")
