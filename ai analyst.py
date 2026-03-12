import anthropic, json, os

try:
    import streamlit as st
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

SYSTEM = """You are a Senior BI Analyst specialising in shipping and maritime commercial operations 
across East African trade lanes. You understand vessel utilization, TEU economics, cargo mix 
optimisation, bunker costs, port productivity, and freight rate dynamics.
Tone: Professional, commercial, data-driven. Use shipping terminology naturally.
Format: Bullet points, bold key findings. Under 300 words. Be specific to the data."""

def analyze_shipping(prompt: str, context: dict) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=500,
        system=SYSTEM,
        messages=[{"role":"user","content":
            f"Fleet context:\n{json.dumps(context, indent=2, default=str)}\n\nQuery: {prompt}"}]
    )
    return msg.content[0].text

def forecast_volumes(monthly_data: list) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=400,
        system=SYSTEM,
        messages=[{"role":"user","content":
            f"Monthly TEU/revenue data (last 12 months):\n{json.dumps(monthly_data, indent=2, default=str)}\n\n"
            "Provide: 1) Key trend observations, 2) Demand drivers to watch on East Africa lanes, "
            "3) 3-month volume outlook with confidence level. Under 250 words."}]
    )
    return msg.content[0].text

def competitor_intelligence(market_data: list) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=400,
        system=SYSTEM,
        messages=[{"role":"user","content":
            f"Market rate and share data by trade lane:\n{json.dumps(market_data, indent=2, default=str)}\n\n"
            "Provide: 1) Where we are over/under-priced vs market, "
            "2) Lanes where we should defend or grow share, "
            "3) Top 2 competitive threats. Under 250 words."}]
    )
    return msg.content[0].textss