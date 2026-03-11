import anthropic
import json
import os

try:
    import streamlit as st
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

SYSTEM = """You are a Senior Business Intelligence Analyst specialising in shipping and maritime commercial operations for an East African container line.

Your expertise covers:
- Vessel utilization and capacity optimization
- Freight rate analysis and pricing strategy  
- Cargo mix optimization (Reefer, Hazmat, OOG, Dry Bulk)
- Trade lane revenue and margin performance
- CRM pipeline management and win-rate analysis
- Volume forecasting and seasonal demand patterns
- Competitor intelligence (Maersk, MSC, CMA CGM, Hapag-Lloyd, Evergreen)
- Port operations: Mombasa, Dar es Salaam, Djibouti, Durban

Tone: Concise, commercial, data-driven. Use shipping industry terminology naturally.
Format: Use bullet points and bold key findings. Keep responses under 300 words."""


def analyze_with_ai(prompt: str, context: dict) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content":
            f"Portfolio context:\n{json.dumps(context, indent=2, default=str)}\n\nQuery: {prompt}"}]
    )
    return msg.content[0].text


def cargo_mix_insight(cargo_stats: list) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=SYSTEM,
        messages=[{"role": "user", "content":
            f"Analyze this cargo mix performance and recommend optimization:\n{json.dumps(cargo_stats, default=str)}\n"
            "Provide: 1) Highest-margin cargo types to prioritize, 2) Underperforming segments, 3) Specific allocation recommendations. Under 250 words."}]
    )
    return msg.content[0].text


def forecast_insight(actuals: list, forecasts: list) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=SYSTEM,
        messages=[{"role": "user", "content":
            f"Actuals:\n{json.dumps(actuals, default=str)}\nForecasts:\n{json.dumps(forecasts, default=str)}\n"
            "Interpret the volume and revenue forecast. Identify seasonal patterns, risks, and commercial actions. Under 250 words."}]
    )
    return msg.content[0].text


def crm_insight(pipeline: list) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=SYSTEM,
        messages=[{"role": "user", "content":
            f"CRM pipeline data:\n{json.dumps(pipeline, default=str)}\n"
            "Identify: 1) Pipeline health and conversion risk, 2) High-value opportunities to prioritize, "
            "3) Deals at risk from competitors, 4) Recommended sales actions. Under 250 words."}]
    )
    return msg.content[0].text