"""
Rule-based scoring engine.
Each lead gets a score (0–100) per ABBK service.
Signals are extracted from scraped data and weighted by service type.
"""
from dataclasses import dataclass, field
from typing import Any

import anthropic

from app.core.config import settings


# ─── Signal weights per service ───────────────────────────────────────────────
# Tweak these values as you learn which signals actually convert.

SIGNAL_WEIGHTS = {
    "solidworks_license": {
        "has_mechanical_engineer":  25,
        "has_cad_designer":         20,
        "is_multinational":         20,
        "is_exporter":              15,
        "under_audit":              20,
        "uses_solidworks_logo":     30,
        "uses_competitor_software": 10,
        "recent_engineering_hire":  15,
        "attended_solidworks_event": 20,
        "funded_by_bailleur":        8,
    },
    "training": {
        "did_technical_training":   20,
        "has_new_engineers":        25,
        "is_growing_headcount":     15,
        "training_budget_signal":   20,
        "school_partnership":       10,
        "recent_funding":           15,
        "sector_requires_certs":    15,
    },
    "other_license": {
        "uses_solidworks_logo":     15,
        "has_mechanical_engineer":  15,
        "is_multinational":         10,
        "under_audit":              15,
        "uses_competitor_software": 20,
        "attended_industry_event":  10,
    },
}


@dataclass
class ScoringResult:
    service_name: str
    score: float                          # 0–100
    signal_breakdown: dict[str, float]    # which signals fired and their contribution
    reasoning: str                        # human-readable explanation


def score_lead(lead_data: dict[str, Any], service_key: str, service_name: str) -> ScoringResult:
    """
    Score a single lead for a single service.
    lead_data: the scraped + enriched data dict from the Lead model.
    """
    weights = SIGNAL_WEIGHTS.get(service_key, {})
    if not weights:
        return ScoringResult(service_name, 0.0, {}, "Unknown service type")

    total_possible = sum(weights.values())
    earned = 0.0
    breakdown = {}

    for signal, weight in weights.items():
        value = lead_data.get(signal, False)
        if value:
            contribution = weight
            earned += contribution
            breakdown[signal] = contribution
        else:
            breakdown[signal] = 0.0

    # Normalize to 0–100
    score = round((earned / total_possible) * 100, 1) if total_possible > 0 else 0.0

    reasoning = _build_reasoning(breakdown, score)
    return ScoringResult(service_name, score, breakdown, reasoning)


def _build_reasoning(breakdown: dict[str, float], score: float) -> str:
    fired = [sig for sig, pts in breakdown.items() if pts > 0]
    missed = [sig for sig, pts in breakdown.items() if pts == 0]
    lines = [f"Score: {score}/100"]
    if fired:
        lines.append("Positive signals: " + ", ".join(fired))
    if missed:
        lines.append("Missing signals: " + ", ".join(missed[:5]))
    return " | ".join(lines)


async def extract_signals_with_ai(scraped_text: str, company_name: str) -> dict[str, bool]:
    """
    Use Claude to extract boolean signals from unstructured scraped text.
    Returns a dict of signal_name → True/False.
    Cached result should be stored in DB to avoid re-calling the API.
    """
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""
You are analyzing scraped data about a company called "{company_name}" to extract sales intelligence signals.

Scraped text:
{scraped_text[:4000]}

Respond with ONLY a valid JSON object (no markdown, no explanation) with these boolean keys:
{{
  "has_mechanical_engineer": bool,
  "has_cad_designer": bool,
  "is_multinational": bool,
  "is_exporter": bool,
  "under_audit": bool,
  "uses_solidworks_logo": bool,
  "uses_competitor_software": bool,
  "recent_engineering_hire": bool,
  "attended_solidworks_event": bool,
  "did_technical_training": bool,
  "has_new_engineers": bool,
  "is_growing_headcount": bool,
  "recent_funding": bool,
  "funded_by_bailleur": bool,
  "school_partnership": bool,
  "sector_requires_certs": bool,
  "attended_industry_event": bool,
  "training_budget_signal": bool
}}
"""
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        return json.loads(response.content[0].text)
    except Exception:
        return {}
