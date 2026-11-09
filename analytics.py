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


ROAS_THRESHOLD = 2.0
CONVERSION_RATE_THRESHOLD = 2.0


def _underperformance_reasons(enriched: dict[str, Any]) -> list[str]:
    """Return human-readable reasons for missed performance thresholds."""
    reasons: list[str] = []
    if enriched["roas"] < ROAS_THRESHOLD:
        reasons.append(f"ROAS {enriched['roas']} is below {ROAS_THRESHOLD}")
    if enriched["conversion_rate_pct"] < CONVERSION_RATE_THRESHOLD:
        reasons.append(
            f"conversion rate {enriched['conversion_rate_pct']}% is below "
            f"{CONVERSION_RATE_THRESHOLD}%"
        )
    return reasons


def recommend_actions(enriched: dict[str, Any]) -> list[str]:
    """Return concise, data-grounded next steps for an enriched campaign."""
    recommendations: list[str] = []
    low_roas = enriched["roas"] < ROAS_THRESHOLD
    low_conversion = enriched["conversion_rate_pct"] < CONVERSION_RATE_THRESHOLD
    zero_engagement = enriched["clicks"] == 0 and enriched["conversions"] == 0

    if zero_engagement:
        recommendations.append(
            "Pause or diagnose delivery: no clicks or conversions yet—"
            "check targeting, creative, and tracking."
        )
        return recommendations

    if low_roas:
        recommendations.append(
            "Tighten audience or creative to improve return on ad spend."
        )
    if low_conversion:
        recommendations.append(
            "Improve landing page, offer, or post-click funnel to raise conversion rate."
        )
    return recommendations


def find_underperforming(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag campaigns below ROAS or conversion-rate thresholds with recommendations."""
    results: list[dict[str, Any]] = []
    for campaign in campaigns:
        enriched = enrich_campaign(campaign)
        reasons = _underperformance_reasons(enriched)
        if not reasons:
            continue
        results.append(
            {
                **enriched,
                "reasons": reasons,
                "recommendations": recommend_actions(enriched),
            }
        )
    return results
