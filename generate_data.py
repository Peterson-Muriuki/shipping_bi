import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

TRADE_LANES = [
    "Mombasa-Dubai", "Mombasa-Shanghai", "Dar-Rotterdam",
    "Mombasa-Mumbai", "Mombasa-Singapore", "Dar-Jeddah",
    "Mombasa-Colombo", "Dar-Shanghai"
]
VESSELS = [
    "MV Kilimanjaro", "MV Serengeti", "MV Rift Valley", "MV Zanzibar Star",
    "MV Coastal Pride", "MV Indian Ocean", "MV Swahili Express", "MV Nairobi Bay"
]
VESSEL_TYPES = {
    "MV Kilimanjaro":"Panamax","MV Serengeti":"Handymax",
    "MV Rift Valley":"Panamax","MV Zanzibar Star":"Feeder",
    "MV Coastal Pride":"Feeder","MV Indian Ocean":"Handymax",
    "MV Swahili Express":"Panamax","MV Nairobi Bay":"Feeder"
}
CAPACITY = {"Panamax":4500,"Handymax":2800,"Feeder":1200}
CARGO_TYPES = ["General Cargo","Reefer","Hazardous","Bulk Dry","Ro-Ro","Project Cargo"]
ORIGIN_PORTS = ["Mombasa","Dar es Salaam","Kisumu","Nakuru","Kampala","Kigali"]
CUSTOMERS = [
    "Kenyan Commodities Ltd","East Africa Traders","Mombasa Freight Co",
    "Gulf Shipping Partners","Dar Logistics","Pan-Africa Cargo",
    "Indian Ocean Lines","Coastal Freight Solutions","SafariCargo Ltd",
    "Nairobi Import House","Kilindini Shippers","Red Sea Carriers",
    "Swahili Coast Trading","Great Lakes Freight","Rift Valley Logistics"
]
COMPETITORS = ["Maersk","MSC","CMA CGM","Hapag-Lloyd","COSCO"]
SALES_REPS = ["Alice K.","Brian M.","Carol N.","David O.","Eva P."]


def generate_voyages(n=800):
    start = datetime(2023, 1, 1)
    records = []
    for i in range(n):
        vessel = random.choice(VESSELS)
        vtype = VESSEL_TYPES[vessel]
        cap = CAPACITY[vtype]
        lane = random.choice(TRADE_LANES)
        dep = start + timedelta(days=random.randint(0, 760))
        voyage_days = random.randint(12, 45)
        freight_rate = np.random.uniform(800, 3200)
        utilization = np.clip(np.random.beta(5, 2), 0.4, 1.0)
        booked_teu = int(cap * utilization)
        fuel_cost = voyage_days * random.uniform(8000, 22000)
        port_cost = random.uniform(15000, 75000)
        other_cost = random.uniform(5000, 20000)
        operating_cost = fuel_cost + port_cost + other_cost
        revenue = booked_teu * freight_rate
        net_margin = revenue - operating_cost
        on_time = 1 if random.random() > 0.18 else 0
        records.append({
            "voyage_id": f"VOY{str(i).zfill(5)}",
            "vessel": vessel,
            "vessel_type": vtype,
            "trade_lane": lane,
            "departure_date": dep,
            "arrival_date": dep + timedelta(days=voyage_days),
            "voyage_days": voyage_days,
            "capacity_teu": cap,
            "booked_teu": booked_teu,
            "utilization_pct": round(utilization * 100, 2),
            "freight_rate_usd": round(freight_rate, 2),
            "revenue_usd": round(revenue, 2),
            "fuel_cost_usd": round(fuel_cost, 2),
            "port_cost_usd": round(port_cost, 2),
            "operating_cost_usd": round(operating_cost, 2),
            "net_margin_usd": round(net_margin, 2),
            "net_margin_pct": round(net_margin / revenue * 100, 2) if revenue > 0 else 0,
            "on_time": on_time,
            "primary_cargo": random.choice(CARGO_TYPES),
            "month": dep.strftime("%Y-%m"),
            "quarter": f"Q{((dep.month-1)//3)+1} {dep.year}",
        })
    df = pd.DataFrame(records)
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    df["arrival_date"]   = pd.to_datetime(df["arrival_date"])
    return df


def generate_cargo(voyages_df, avg_per_voyage=4):
    records = []
    cid = 0
    for _, row in voyages_df.iterrows():
        n = random.randint(2, 6)
        remaining = row["booked_teu"]
        for j in range(n):
            teu = random.randint(20, max(20, remaining // 2)) if j < n-1 else max(10, remaining)
            remaining = max(0, remaining - teu)
            weight_mt = teu * random.uniform(8, 18)
            rate = row["freight_rate_usd"] * random.uniform(0.85, 1.2)
            records.append({
                "cargo_id": f"CGO{str(cid).zfill(6)}",
                "voyage_id": row["voyage_id"],
                "trade_lane": row["trade_lane"],
                "cargo_type": random.choice(CARGO_TYPES),
                "customer": random.choice(CUSTOMERS),
                "origin_port": random.choice(ORIGIN_PORTS),
                "teu": teu,
                "weight_mt": round(weight_mt, 1),
                "freight_rate_usd": round(rate, 2),
                "revenue_usd": round(teu * rate, 2),
                "month": row["month"],
            })
            cid += 1
            if remaining <= 0:
                break
    return pd.DataFrame(records)


def generate_crm(n=400):
    statuses = ["Qualified","Proposal Sent","In Progress","Won","Lost"]
    probs    = [0.20, 0.20, 0.25, 0.20, 0.15]
    prob_map = {"Qualified":0.20,"Proposal Sent":0.40,"In Progress":0.65,"Won":1.0,"Lost":0.0}
    start = datetime(2024, 1, 1)
    records = []
    for i in range(n):
        status = np.random.choice(statuses, p=probs)
        value  = round(np.random.lognormal(11, 0.8), 2)
        prob   = prob_map[status]
        created = start + timedelta(days=random.randint(0, 420))
        records.append({
            "opportunity_id": f"OPP{str(i).zfill(5)}",
            "customer": random.choice(CUSTOMERS),
            "trade_lane": random.choice(TRADE_LANES),
            "cargo_type": random.choice(CARGO_TYPES),
            "status": status,
            "deal_value_usd": value,
            "probability": prob,
            "expected_value_usd": round(value * prob, 2),
            "sales_rep": random.choice(SALES_REPS),
            "competitor": random.choice(COMPETITORS + [None, None]),
            "created_date": created,
            "expected_close": created + timedelta(days=random.randint(14, 180)),
            "month": created.strftime("%Y-%m"),
        })
    df = pd.DataFrame(records)
    df["created_date"]   = pd.to_datetime(df["created_date"])
    df["expected_close"] = pd.to_datetime(df["expected_close"])
    return df


def generate_market(voyages_df):
    start = datetime(2023, 1, 1)
    records = []
    months = [(start + timedelta(days=30*i)).strftime("%Y-%m") for i in range(25)]
    for month in months:
        for lane in TRADE_LANES:
            our_share = round(np.random.uniform(8, 28), 2)
            our_rate  = round(np.random.uniform(750, 3300), 2)
            for comp in COMPETITORS:
                comp_rate = round(np.random.uniform(700, 3500), 2)
                records.append({
                    "month": month,
                    "trade_lane": lane,
                    "competitor": comp,
                    "our_rate_usd": our_rate,
                    "competitor_rate_usd": comp_rate,
                    "rate_advantage": round(our_rate - comp_rate, 2),
                    "our_market_share_pct": our_share,
                    "competitor_share_pct": round(np.random.uniform(5, 35), 2),
                    "market_volume_teu": random.randint(800, 4000),
                    "our_ontime_pct": round(np.random.uniform(75, 96), 2),
                    "comp_ontime_pct": round(np.random.uniform(72, 98), 2),
                })
    return pd.DataFrame(records)


def get_all_data():
    voyages = generate_voyages(800)
    cargo   = generate_cargo(voyages)
    crm     = generate_crm(400)
    market  = generate_market(voyages)
    return voyages, cargo, crm, market