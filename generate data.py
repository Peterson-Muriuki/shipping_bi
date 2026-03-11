import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

TRADE_LANES = {
    "East Africa – Asia":        {"base_rate": 1850, "vol": 320, "distance_nm": 4800},
    "East Africa – Europe":      {"base_rate": 2200, "vol": 410, "distance_nm": 7200},
    "East Africa – Middle East": {"base_rate": 1100, "vol": 180, "distance_nm": 2100},
    "Intra-Africa":              {"base_rate": 750,  "vol": 120, "distance_nm": 1400},
    "East Africa – Americas":    {"base_rate": 3100, "vol": 520, "distance_nm": 9800},
}

VESSELS = [
    {"name": "MV Kilimanjaro",  "teu": 3500, "type": "Feeder",   "flag": "KE", "age": 8},
    {"name": "MV Mombasa Star", "teu": 5200, "type": "Regional", "flag": "SG", "age": 5},
    {"name": "MV Rift Valley",  "teu": 2800, "type": "Feeder",   "flag": "KE", "age": 12},
    {"name": "MV Serengeti",    "teu": 7800, "type": "Deep Sea", "flag": "MH", "age": 3},
    {"name": "MV Nairobi Bay",  "teu": 1900, "type": "Coastal",  "flag": "KE", "age": 15},
    {"name": "MV Zanzibar",     "teu": 4100, "type": "Regional", "flag": "TZ", "age": 7},
]

CARGO_TYPES   = ["Dry Bulk", "Reefer", "Hazmat", "OOG", "General Cargo", "Liquid Bulk"]
CARGO_MARGINS = {"Dry Bulk": 0.18, "Reefer": 0.34, "Hazmat": 0.42, "OOG": 0.38, "General Cargo": 0.22, "Liquid Bulk": 0.29}
CUSTOMERS     = [f"Customer_{chr(65+i)}" for i in range(20)]
COMPETITORS   = ["Maersk Line", "MSC", "CMA CGM", "Hapag-Lloyd", "Evergreen"]
PORTS         = ["Mombasa", "Dar es Salaam", "Djibouti", "Durban", "Port Louis", "Singapore", "Rotterdam", "Dubai", "Shanghai", "New York"]


def generate_voyages(n=800):
    records = []
    start = datetime(2023, 1, 1)
    for i in range(n):
        vessel    = random.choice(VESSELS)
        lane      = random.choice(list(TRADE_LANES.keys()))
        lane_info = TRADE_LANES[lane]
        depart    = start + timedelta(days=random.randint(0, 730))
        duration  = int(lane_info["distance_nm"] / random.uniform(260, 320))
        arrive    = depart + timedelta(days=duration)
        util      = float(np.clip(np.random.beta(5, 2), 0.45, 1.0))
        teu_loaded= int(vessel["teu"] * util)
        base_rate = lane_info["base_rate"] + float(np.random.normal(0, lane_info["vol"]))
        fuel_cost = lane_info["distance_nm"] * random.uniform(0.38, 0.55) * (vessel["teu"] / 1000)
        port_cost = random.uniform(18000, 65000)
        revenue   = teu_loaded * max(base_rate, 500)
        opex      = fuel_cost + port_cost + random.uniform(12000, 45000)
        records.append({
            "voyage_id":        f"VYG{str(i+1).zfill(5)}",
            "vessel_name":      vessel["name"],
            "vessel_type":      vessel["type"],
            "vessel_teu":       vessel["teu"],
            "trade_lane":       lane,
            "origin":           random.choice(PORTS[:5]),
            "destination":      random.choice(PORTS[3:]),
            "departure_date":   depart,
            "arrival_date":     arrive,
            "voyage_days":      duration,
            "teu_capacity":     vessel["teu"],
            "teu_loaded":       teu_loaded,
            "utilization_pct":  round(util * 100, 2),
            "freight_rate_usd": round(max(base_rate, 500), 2),
            "revenue_usd":      round(revenue, 2),
            "fuel_cost_usd":    round(fuel_cost, 2),
            "port_cost_usd":    round(port_cost, 2),
            "total_opex_usd":   round(opex, 2),
            "gross_profit_usd": round(revenue - opex, 2),
            "margin_pct":       round((revenue - opex) / revenue * 100, 2) if revenue > 0 else 0,
        })
    df = pd.DataFrame(records)
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    df["arrival_date"]   = pd.to_datetime(df["arrival_date"])
    df["month"]   = df["departure_date"].dt.to_period("M").astype(str)
    df["quarter"] = df["departure_date"].dt.to_period("Q").astype(str)
    df["year"]    = df["departure_date"].dt.year
    return df


def generate_cargo_manifest(voyages_df, n_per_voyage=6):
    records = []
    for _, v in voyages_df.iterrows():
        remaining = int(v["teu_loaded"])
        n = random.randint(3, n_per_voyage)
        for j in range(n):
            cargo_type = np.random.choice(CARGO_TYPES, p=[0.35, 0.18, 0.08, 0.07, 0.22, 0.10])
            share  = random.uniform(0.1, 0.4)
            teu    = max(20, int(remaining * share))
            remaining = max(0, remaining - teu)
            margin = CARGO_MARGINS[cargo_type] + float(np.random.normal(0, 0.04))
            rate   = float(v["freight_rate_usd"]) * random.uniform(0.85, 1.25)
            rev    = teu * rate
            records.append({
                "voyage_id":        v["voyage_id"],
                "booking_id":       f"BK{str(len(records)+1).zfill(7)}",
                "customer":         random.choice(CUSTOMERS),
                "cargo_type":       cargo_type,
                "teu_booked":       teu,
                "freight_rate_usd": round(rate, 2),
                "revenue_usd":      round(rev, 2),
                "margin_pct":       round(float(np.clip(margin * 100, 5, 65)), 2),
                "gross_profit_usd": round(rev * float(np.clip(margin, 0.05, 0.65)), 2),
                "trade_lane":       v["trade_lane"],
                "month":            v["month"],
                "departure_date":   v["departure_date"],
            })
    return pd.DataFrame(records)


def generate_crm_pipeline(n=350):
    stages      = ["Prospect", "Qualified", "Proposal Sent", "Negotiation", "Closed Won", "Closed Lost"]
    stage_probs = [0.25, 0.20, 0.20, 0.15, 0.12, 0.08]
    win_prob    = {"Prospect":0.10,"Qualified":0.25,"Proposal Sent":0.45,
                   "Negotiation":0.70,"Closed Won":1.0,"Closed Lost":0.0}
    records = []
    start = datetime(2023, 6, 1)
    for i in range(n):
        stage = np.random.choice(stages, p=stage_probs)
        lane  = random.choice(list(TRADE_LANES.keys()))
        teu   = random.randint(50, 2000)
        rate  = TRADE_LANES[lane]["base_rate"] * random.uniform(0.9, 1.3)
        value = teu * rate * random.randint(1, 12)
        records.append({
            "opp_id":             f"OPP{str(i+1).zfill(5)}",
            "customer":           random.choice(CUSTOMERS),
            "trade_lane":         lane,
            "stage":              stage,
            "teu_volume":         teu,
            "annual_value_usd":   round(value, 2),
            "win_probability":    win_prob[stage],
            "weighted_value_usd": round(value * win_prob[stage], 2),
            "created_date":       start + timedelta(days=random.randint(0, 600)),
            "sales_rep":          random.choice(["Alice K.","Brian M.","Carol N.","David O.","Eve P."]),
            "competitor":         random.choice(COMPETITORS + [None, None]),
            "days_in_stage":      random.randint(1, 120),
        })
    df = pd.DataFrame(records)
    df["created_date"] = pd.to_datetime(df["created_date"])
    return df


def generate_market_intelligence(months=24):
    records = []
    start = datetime(2023, 1, 1)
    for m in range(months):
        dt = start + pd.DateOffset(months=m)
        for lane in TRADE_LANES:
            base = TRADE_LANES[lane]["base_rate"]
            for comp in COMPETITORS + ["Our Line"]:
                noise = float(np.random.normal(0, base * 0.08))
                if comp == "Our Line":
                    rate = base + noise
                elif comp == "Maersk Line":
                    rate = base * 1.05 + noise
                elif comp == "MSC":
                    rate = base * 0.97 + noise
                else:
                    rate = base * random.uniform(0.93, 1.08) + noise
                records.append({
                    "month":           dt.strftime("%Y-%m"),
                    "trade_lane":      lane,
                    "carrier":         comp,
                    "avg_rate_usd":    round(max(rate, 400), 2),
                    "market_share_pct":round(random.uniform(5, 35), 1),
                })
    return pd.DataFrame(records)


def generate_volume_forecast(voyages_df):
    monthly = voyages_df.groupby("month").agg(
        actual_teu=("teu_loaded","sum"),
        actual_revenue=("revenue_usd","sum"),
        voyages=("voyage_id","count")
    ).reset_index().sort_values("month")
    n = len(monthly)
    trend = np.polyfit(range(n), monthly["actual_teu"], 1)
    forecast_months = pd.period_range(
        start=pd.Period(monthly["month"].iloc[-1]) + 1, periods=6, freq="M"
    ).astype(str)
    forecasts = []
    for i, fm in enumerate(forecast_months):
        base     = float(np.polyval(trend, n + i))
        seasonal = 1 + 0.08 * np.sin(2 * np.pi * (n + i) / 12)
        rev_per_teu = float(monthly["actual_revenue"].iloc[-1]) / float(monthly["actual_teu"].iloc[-1])
        forecasts.append({
            "month":            fm,
            "forecast_teu":     int(base * seasonal),
            "forecast_revenue": int(base * seasonal * rev_per_teu),
            "lower_bound":      int(base * seasonal * 0.88),
            "upper_bound":      int(base * seasonal * 1.12),
            "is_forecast":      True,
        })
    monthly["is_forecast"]      = False
    monthly["forecast_teu"]     = monthly["actual_teu"]
    monthly["lower_bound"]      = monthly["actual_teu"]
    monthly["upper_bound"]      = monthly["actual_teu"]
    return monthly, pd.DataFrame(forecasts)


def get_all_data():
    voyages   = generate_voyages(800)
    cargo     = generate_cargo_manifest(voyages)
    crm       = generate_crm_pipeline(350)
    market    = generate_market_intelligence(24)
    actuals, forecasts = generate_volume_forecast(voyages)
    return voyages, cargo, crm, market, actuals, forecasts