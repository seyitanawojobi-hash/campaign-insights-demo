# Campaign Insights Demo

A **fictional Adobe-inspired internal application** for a Cursor developer-enablement demonstration. This is **not** an Adobe product or affiliated repository.

The app serves sample marketing-campaign performance data and computes simple campaign metrics. The requested feature—**flag underperforming campaigns and suggest next steps**—is intentionally **not implemented** so a developer can use Cursor Ask → Plan → Agent → Test to build it.

## Files

- `app.py` — FastAPI endpoints
- `analytics.py` — campaign metric calculations
- `campaigns.json` — fictional sample data
- `test_analytics.py` — existing regression tests
- `README.md` — setup and demo instructions

## Run locally

Requires Python 3.10+.

```bash
python -m pip install fastapi uvicorn pytest httpx
python -m pytest -q
python -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

Existing endpoints:
- `GET /health`
- `GET /campaigns`
- `GET /campaigns/{campaign_id}`
- `GET /summary`

## Cursor demo: 8 minutes

**Scenario:** You are a new engineer joining the team. Marketing operations wants an endpoint that highlights underperforming campaigns and explains why they need attention.

1. **Ask:** `Explain this repository's architecture, how campaign metrics are calculated, and which files matter for adding an underperforming-campaign endpoint. Do not edit files.`
2. **Plan:** `Plan a GET /campaigns/underperforming endpoint that flags campaigns with ROAS below 2.0 or conversion rate below 2%, and returns concise, data-grounded recommendations. Reuse existing analytics functions, handle zero denominators, and add tests. Do not edit files yet.`
3. **Agent:** Review and approve the plan, then implement it.
4. **Validate:** Run tests, inspect the diff, and try the endpoint in `/docs`.
5. **Review:** Explain what tests prove and what still requires human review before a PR.

**Important design detail:** The existing dynamic route `/campaigns/{campaign_id}` could shadow `/campaigns/underperforming` if the new static route is registered after it. Ask Cursor to consider route ordering.

## Metrics

- CTR = clicks / impressions × 100
- Conversion rate = conversions / clicks × 100
- ROAS = revenue / spend

Zero denominators return `0.0` instead of errors. All values are illustrative; no customer data is included.
