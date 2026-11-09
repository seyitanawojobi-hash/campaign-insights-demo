"""Baseline tests; new-feature tests belong here too."""

from fastapi.testclient import TestClient

from analytics import enrich_campaign, safe_ratio, summarize_campaigns
from app import app

client = TestClient(app)


def test_safe_ratio_handles_zero_denominator():
    assert safe_ratio(10, 0) == 0.0
    assert safe_ratio(6, 3) == 2.0


def test_enrich_campaign_calculates_metrics():
    result = enrich_campaign({
        "id": "demo", "name": "Demo", "impressions": 1000,
        "clicks": 100, "conversions": 5, "spend": 100.0,
        "revenue": 300.0,
    })
    assert result["ctr_pct"] == 10.0
    assert result["conversion_rate_pct"] == 5.0
    assert result["roas"] == 3.0


def test_summary_uses_weighted_totals():
    campaigns = [
        {"impressions": 100, "clicks": 10, "conversions": 1, "spend": 10, "revenue": 20},
        {"impressions": 300, "clicks": 30, "conversions": 3, "spend": 30, "revenue": 90},
    ]
    result = summarize_campaigns(campaigns)
    assert result["campaign_count"] == 2
    assert result["roas"] == 2.75
    assert result["conversion_rate_pct"] == 10.0


def test_api_lists_campaigns():
    response = client.get("/campaigns")
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["roas"] == 4.0


def test_api_campaign_lookup_and_not_found():
    assert client.get("/campaigns/email-nurture").status_code == 200
    assert client.get("/campaigns/missing").status_code == 404


def test_api_summary_and_health():
    assert client.get("/health").json() == {"status": "ok"}
    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json()["campaign_count"] == 4
