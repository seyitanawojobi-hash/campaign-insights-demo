"""Baseline tests; new-feature tests belong here too."""

from fastapi.testclient import TestClient

from analytics import (
    enrich_campaign,
    find_underperforming,
    safe_ratio,
    summarize_campaigns,
)
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


def _campaign(**overrides):
    base = {
        "id": "c1",
        "name": "Campaign",
        "channel": "paid_social",
        "impressions": 1000,
        "clicks": 100,
        "conversions": 5,
        "spend": 100.0,
        "revenue": 300.0,
    }
    base.update(overrides)
    return base


def test_find_underperforming_low_roas_only():
    # High conversion (10%), low ROAS (1.0)
    campaigns = [_campaign(conversions=10, revenue=100.0)]
    results = find_underperforming(campaigns)
    assert len(results) == 1
    assert results[0]["roas"] == 1.0
    assert results[0]["conversion_rate_pct"] == 10.0
    assert any("ROAS" in reason for reason in results[0]["reasons"])
    assert not any("conversion rate" in reason for reason in results[0]["reasons"])
    assert results[0]["recommendations"]


def test_find_underperforming_low_conversion_only():
    # Low conversion (1%), healthy ROAS (3.0)
    campaigns = [_campaign(conversions=1, revenue=300.0)]
    results = find_underperforming(campaigns)
    assert len(results) == 1
    assert results[0]["conversion_rate_pct"] == 1.0
    assert results[0]["roas"] == 3.0
    assert any("conversion rate" in reason for reason in results[0]["reasons"])
    assert not any("ROAS" in reason for reason in results[0]["reasons"])
    assert results[0]["recommendations"]


def test_find_underperforming_both_thresholds():
    campaigns = [_campaign(conversions=1, revenue=100.0)]
    results = find_underperforming(campaigns)
    assert len(results) == 1
    assert len(results[0]["reasons"]) == 2
    assert len(results[0]["recommendations"]) >= 1


def test_find_underperforming_excludes_healthy():
    campaigns = [_campaign()]  # ROAS 3.0, conversion 5%
    assert find_underperforming(campaigns) == []


def test_find_underperforming_zero_clicks():
    campaigns = [_campaign(clicks=0, conversions=0, revenue=0.0)]
    results = find_underperforming(campaigns)
    assert len(results) == 1
    assert results[0]["conversion_rate_pct"] == 0.0
    assert results[0]["roas"] == 0.0
    assert results[0]["reasons"]
    assert results[0]["recommendations"]


def test_api_underperforming_campaigns():
    response = client.get("/campaigns/underperforming")
    assert response.status_code == 200
    payload = response.json()
    ids = {item["id"] for item in payload}
    assert ids == {"retargeting-q3", "new-audience-test"}
    for item in payload:
        assert item["reasons"]
        assert item["recommendations"]
        assert "roas" in item
        assert "conversion_rate_pct" in item


def test_api_underperforming_route_not_shadowed():
    response = client.get("/campaigns/underperforming")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_served_at_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Campaign Insights" in body
    assert "Underperforming Campaigns" in body
    assert "fetch(\"/campaigns\")" in body
    assert "fetch(\"/summary\")" in body
    assert "fetch(\"/campaigns/underperforming\")" in body


def test_dashboard_does_not_break_api_routes():
    assert client.get("/health").status_code == 200
    assert client.get("/campaigns").status_code == 200
    assert client.get("/campaigns/underperforming").status_code == 200
    assert client.get("/summary").status_code == 200
