"""Small fictional campaign analytics API."""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from analytics import enrich_campaign, summarize_campaigns

app = FastAPI(title="Campaign Insights Demo", version="0.1.0")
DATA_FILE = Path(__file__).with_name("campaigns.json")


def load_campaigns() -> list[dict]:
    """Load bundled fictional campaign data."""
    with DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/campaigns")
def list_campaigns() -> list[dict]:
    return [enrich_campaign(item) for item in load_campaigns()]


@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str) -> dict:
    for campaign in load_campaigns():
        if campaign["id"] == campaign_id:
            return enrich_campaign(campaign)
    raise HTTPException(status_code=404, detail="Campaign not found")


@app.get("/summary")
def summary() -> dict:
    return summarize_campaigns(load_campaigns())
