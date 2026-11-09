"""Pure functions for campaign performance metrics."""

from typing import Any


def safe_ratio(numerator: float, denominator: float) -> float:
    """Return zero for a zero denominator, otherwise numerator / denominator."""
    return numerator / denominator if denominator else 0.0


def enrich_campaign(campaign: dict[str, Any]) -> dict[str, Any]:
    """Return a campaign with rounded, computed performance metrics."""
    impressions = campaign["impressions"]
    clicks = campaign["clicks"]
    conversions = campaign["conversions"]
    spend = campaign["spend"]
    revenue = campaign["revenue"]

    return {
        **campaign,
        "ctr_pct": round(safe_ratio(clicks, impressions) * 100, 2),
        "conversion_rate_pct": round(safe_ratio(conversions, clicks) * 100, 2),
        "roas": round(safe_ratio(revenue, spend), 2),
    }


def summarize_campaigns(campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate totals and compute weighted performance metrics."""
    totals = {
        field: sum(campaign[field] for campaign in campaigns)
        for field in ("impressions", "clicks", "conversions", "spend", "revenue")
    }
    return {"campaign_count": len(campaigns), **enrich_campaign(totals)}
