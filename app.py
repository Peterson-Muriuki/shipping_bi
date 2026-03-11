import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import duckdb, sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.generate_data import get_all_data
from utils.ai_analyst import analyze_shipping, forecast_volumes, competitor_intelligence

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Shipping BI Platform", page_icon="🚢",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0A0F1E; }
section[data-testid="stSidebar"] {
    background: #0D1526 !important;
    border-right: 1px solid #1E2D45;
}

.hero {
    background: linear-gradient(135deg, #002952 0%, #0A0F1E 55%);
    border: 1px solid #0EA5E9;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "🚢";
    position: absolute;
    right: 36px; top: 20px;
    font-size: 4rem;
    opacity: 0.15;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #F0F9FF;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
}
.hero p { color: #7DD3FC; font-size: 0.95rem; margin: 0; }

.kcard {
    background: linear-gradient(135deg, #0F1F38 0%, #0D1526 100%);
    border: 1px solid #1E3A5F;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 4px 0;
}
.kcard .val {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #F0F9FF;
    line-height: 1;
}
.kcard .lbl {
    font-size: 0.7rem;
    color: #64748B;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 4px;
}
.kcard .dl { font-size: 0.8rem; margin-top: 5px; font-weight: 500; }
.dg { color: #34D399; }
.dr { color: #F87171; }

.sec-h {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #F0F9FF;
    margin: 28px 0 4px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #0EA5E9;
}
.sec-s { color: #64748B; font-size: 0.82rem; margin-bottom: 18px; }

.ai-box {
    background: linear-gradient(135deg, #001D3D 0%, #0A0F1E 100%);
    border: 1px solid #0EA5E9;
    border-left: 4px solid #38BDF8;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 14px 0;
    font-size: 0.88rem;
    color: #BAE6FD;
    line-height: 1.75;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0D1526; border-radius: 8px; padding: 4px; gap: 3px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 6px;
    color: #64748B; font-size: 0.83rem; font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #1E2D45 !important; color: #38BDF8 !important;
}
h1,h2,h3,p,label,.stMarkdown { color: #F1F5F9; }
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    return get_all_data()

voyages, cargo, crm, market = load()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚢 Shipping BI Platform")
    st.markdown("<hr style='border-color:#1E2D45;margin:8px 0 14px'>", unsafe_allow_html=True)
    lanes = ["All"] + sorted(voyages["trade_lane"].unique().tolist())
    sel_lane = st.selectbox("🗺️ Trade Lane", lanes)
    vessels_list = ["All"] + sorted(voyages["vessel"].unique().tolist())
    sel_vessel = st.selectbox("🚢 Vessel", vessels_list)
    quarters = ["All"] + sorted(voyages["quarter"].unique().tolist())
    sel_q = st.selectbox("📅 Quarter", quarters)
    st.markdown("<hr style='border-color:#1E2D45;margin:14px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569;font-size:0.73rem;'>BI Analyst · Shipping Industry<br>Built with Streamlit + Claude AI</p>", unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
fv = voyages.copy()
if sel_lane != "All": fv = fv[fv["trade_lane"] == sel_lane]
if sel_vessel != "All": fv = fv[fv["vessel"] == sel_vessel]
if sel_q != "All": fv = fv[fv["quarter"] == sel_q]

fc = cargo[cargo["voyage_id"].isin(fv["voyage_id"])] if len(fv) < len(voyages) else cargo.copy()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_rev = fv["revenue_usd"].sum()
avg_util = fv["utilization_pct"].mean()
avg_margin = fv["net_margin_pct"].mean()
total_teu = fv["booked_teu"].sum()
avg_rate = fv["freight_rate_usd"].mean()
on_time_pct = fv["on_time"].mean() * 100

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚓ Shipping BI Intelligence Platform</h1>
  <p>East Africa Trade Lanes · Voyage Optimization · Revenue Analytics · Market Intelligence · CRM Pipeline</p>
</div>""", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
kpis = [
    (c1, f"${total_rev/1e6:.1f}M", "Total Revenue", f"{len(fv)} voyages", "g"),
    (c2, f"{avg_util:.1f}%",        "Avg Utilization", "Capacity fill rate", "g" if avg_util>80 else "r"),
    (c3, f"{avg_margin:.1f}%",      "Net Margin",      "Rev minus op-cost",  "g" if avg_margin>15 else "r"),
    (c4, f"{total_teu:,}",          "Total TEU Booked","Cargo volume",       "g"),
    (c5, f"${avg_rate:,.0f}",       "Avg Freight Rate","Per TEU (USD)",      "g" if avg_rate>1500 else "r"),
    (c6, f"{on_time_pct:.1f}%",     "On-Time Departure","Schedule reliability","g" if on_time_pct>80 else "r"),
]
for col,val,lbl,delta,s in kpis:
    with col:
        dc = "dg" if s=="g" else "dr"
        ic = "▲" if s=="g" else "▼"
        st.markdown(f"""<div class="kcard">
            <div class="val">{val}</div><div class="lbl">{lbl}</div>
            <div class="dl {dc}">{ic} {delta}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHART THEME ───────────────────────────────────────────────────────────────
PD = dict(paper_bgcolor="#0D1526", plot_bgcolor="#0A0F1E",
          font=dict(color="#94A3B8", family="Inter", size=12),
          xaxis=dict(gridcolor="#1E2D45", linecolor="#1E3A5F", tickfont=dict(color="#64748B")),
          yaxis=dict(gridcolor="#1E2D45", linecolor="#1E3A5F", tickfont=dict(color="#64748B")))

BLUE   = "#38BDF8"
TEAL   = "#2DD4BF"
YELLOW = "#FCD34D"
RED    = "#F87171"
GREEN  = "#34D399"
PURPLE = "#A78BFA"

# ── TABS ─────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5,t6,t7 = st.tabs([
    "⚓ Voyage Overview",
    "📦 Cargo Mix",
    "💰 Revenue & Margin",
    "📈 Volume Forecast",
    "🎯 CRM Pipeline",
    "🌍 Market Intelligence",
    "🤖 AI Analyst",
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — VOYAGE OVERVIEW
# ════════════════════════════════════════════════════════════════════
with t1:
    st.markdown('<div class="sec-h">Voyage Performance Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Vessel utilization, on-time performance, and trade lane efficiency across the fleet</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        # Utilization by vessel
        util_v = fv.groupby("vessel").agg(avg_util=("utilization_pct","mean"),
                                           voyages=("voyage_id","count")).reset_index().sort_values("avg_util")
        fig = go.Figure(go.Bar(x=util_v["avg_util"], y=util_v["vessel"], orientation="h",
            marker=dict(color=util_v["avg_util"],
                        colorscale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
                        colorbar=dict(title="Util %")),
            text=[f"{v:.1f}%" for v in util_v["avg_util"]], textposition="auto"))
        fig.update_layout(title="Avg Utilization by Vessel", **PD, height=340,
                          xaxis_title="Utilization %")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Utilization by trade lane
        util_l = fv.groupby("trade_lane").agg(avg_util=("utilization_pct","mean"),
                                               revenue=("revenue_usd","sum")).reset_index()
        fig = px.bar(util_l, x="trade_lane", y="avg_util", color="revenue",
                     color_continuous_scale=[[0,"#0F2A4A"],[1,BLUE]],
                     labels={"avg_util":"Avg Utilization %","trade_lane":""},
                     title="Utilization & Revenue by Trade Lane")
        fig.update_layout(**PD, height=340)
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        # Monthly utilization trend
        mo = fv.groupby("month").agg(avg_util=("utilization_pct","mean"),
                                      revenue=("revenue_usd","sum"),
                                      voyages=("voyage_id","count")).reset_index().sort_values("month")
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=mo["month"], y=mo["revenue"]/1e3, name="Revenue ($K)",
                             marker_color=BLUE, opacity=0.65), secondary_y=False)
        fig.add_trace(go.Scatter(x=mo["month"], y=mo["avg_util"], name="Utilization %",
                                 line=dict(color=YELLOW, width=2.5), mode="lines+markers"), secondary_y=True)
        fig.update_layout(title="Monthly Revenue & Utilization Trend", **PD, height=340,
                          legend=dict(orientation="h", y=1.1))
        fig.update_yaxes(title_text="Revenue ($K)", secondary_y=False)
        fig.update_yaxes(title_text="Utilization %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # On-time vs late by lane
        ot = fv.groupby("trade_lane")["on_time"].agg(["sum","count"]).reset_index()
        ot.columns = ["trade_lane","on_time","total"]
        ot["late"] = ot["total"] - ot["on_time"]
        ot["on_time_pct"] = ot["on_time"]/ot["total"]*100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ot["trade_lane"], y=ot["on_time_pct"], name="On Time",
                             marker_color=GREEN))
        fig.add_trace(go.Bar(x=ot["trade_lane"], y=100-ot["on_time_pct"], name="Delayed",
                             marker_color=RED))
        fig.update_layout(title="On-Time Performance by Trade Lane", barmode="stack",
                          **PD, height=340, yaxis_title="% of Voyages")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    # Utilization scatter
    fig = px.scatter(fv.sample(min(300,len(fv)), random_state=1),
                     x="booked_teu", y="freight_rate_usd",
                     color="net_margin_pct", size="utilization_pct",
                     color_continuous_scale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
                     facet_col="trade_lane" if sel_lane=="All" else None,
                     labels={"booked_teu":"Booked TEU","freight_rate_usd":"Freight Rate (USD)"},
                     title="TEU Volume vs Freight Rate (coloured by Net Margin %)")
    fig.update_layout(**PD, height=380)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 2 — CARGO MIX OPTIMISATION
# ════════════════════════════════════════════════════════════════════
with t2:
    st.markdown('<div class="sec-h">Cargo Mix & Allocation Optimisation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Cargo type profitability, allocation by trade lane, and revenue per metric tonne analysis</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        cm = fc.groupby("cargo_type").agg(revenue=("revenue_usd","sum"),
                                           weight=("weight_mt","sum"),
                                           shipments=("cargo_id","count")).reset_index()
        cm["rev_per_mt"] = cm["revenue"]/cm["weight"]
        colors = [BLUE, TEAL, YELLOW, RED, GREEN, PURPLE]
        fig = go.Figure(go.Pie(labels=cm["cargo_type"], values=cm["revenue"],
                                hole=0.55,
                                marker_colors=colors,
                                textinfo="label+percent",
                                textfont=dict(size=11, color="#F1F5F9")))
        fig.update_layout(title="Revenue Share by Cargo Type", **PD, height=340,
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure(go.Bar(x=cm["cargo_type"], y=cm["rev_per_mt"],
                                marker=dict(color=cm["rev_per_mt"],
                                            colorscale=[[0,"#0F2A4A"],[0.4,BLUE],[1,TEAL]]),
                                text=[f"${v:.0f}" for v in cm["rev_per_mt"]],
                                textposition="auto"))
        fig.update_layout(title="Revenue per Metric Tonne by Cargo Type",
                          **PD, height=340, yaxis_title="USD/MT")
        st.plotly_chart(fig, use_container_width=True)

    # Cargo mix heatmap: type x lane
    hm = fc.groupby(["trade_lane","cargo_type"])["revenue_usd"].sum().unstack(fill_value=0)
    fig = go.Figure(go.Heatmap(z=hm.values, x=hm.columns.tolist(), y=hm.index.tolist(),
                                colorscale=[[0,"#0A0F1E"],[0.3,"#0F2A4A"],[0.7,BLUE],[1,TEAL]],
                                text=[[f"${v/1e3:.0f}K" for v in row] for row in hm.values],
                                texttemplate="%{text}",
                                colorbar=dict(title="Revenue USD")))
    fig.update_layout(title="Cargo Revenue Heatmap: Trade Lane × Cargo Type",
                      **PD, height=380)
    st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        # Top customers by cargo revenue
        top_cust = fc.groupby("customer")["revenue_usd"].sum().nlargest(12).reset_index()
        fig = go.Figure(go.Bar(x=top_cust["revenue_usd"]/1e3, y=top_cust["customer"],
                                orientation="h", marker_color=BLUE,
                                text=[f"${v:.0f}K" for v in top_cust["revenue_usd"]/1e3],
                                textposition="auto"))
        fig.update_layout(title="Top 12 Customers by Cargo Revenue",
                          **PD, height=380, xaxis_title="Revenue ($K)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Cargo volume by origin port
        op = fc.groupby("origin_port")["weight_mt"].sum().reset_index().sort_values("weight_mt")
        fig = go.Figure(go.Bar(x=op["weight_mt"], y=op["origin_port"],
                                orientation="h",
                                marker=dict(color=op["weight_mt"],
                                            colorscale=[[0,"#0F2A4A"],[1,TEAL]]),
                                text=[f"{v:,.0f} MT" for v in op["weight_mt"]],
                                textposition="auto"))
        fig.update_layout(title="Cargo Volume by Origin Port (MT)",
                          **PD, height=380, xaxis_title="Weight (MT)")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 3 — REVENUE & MARGIN
# ════════════════════════════════════════════════════════════════════
with t3:
    st.markdown('<div class="sec-h">Revenue & Financial Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">P&L breakdown, margin analysis, freight rate benchmarking, and cost structure</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        # Waterfall: revenue vs costs
        avg_rev = fv["revenue_usd"].mean()
        avg_fuel = fv["fuel_cost_usd"].mean()
        avg_port = fv["port_cost_usd"].mean()
        avg_other = fv["operating_cost_usd"].mean() - avg_fuel - avg_port
        avg_net = avg_rev - avg_fuel - avg_port - avg_other
        fig = go.Figure(go.Waterfall(
            name="P&L", orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Freight Revenue","Fuel Cost","Port Costs","Other Opex","Net Profit"],
            y=[avg_rev, -avg_fuel, -avg_port, -avg_other, 0],
            connector=dict(line=dict(color="#1E2D45")),
            decreasing=dict(marker=dict(color=RED)),
            increasing=dict(marker=dict(color=GREEN)),
            totals=dict(marker=dict(color=BLUE)),
            text=[f"${v/1e3:.0f}K" for v in [avg_rev,-avg_fuel,-avg_port,-avg_other,avg_net]],
            textposition="outside"
        ))
        fig.update_layout(title="Avg P&L per Voyage (Waterfall)", **PD, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Margin by lane
        ml = fv.groupby("trade_lane").agg(
            avg_margin=("net_margin_pct","mean"),
            revenue=("revenue_usd","sum"),
            voyages=("voyage_id","count")
        ).reset_index().sort_values("avg_margin")
        fig = go.Figure(go.Bar(x=ml["avg_margin"], y=ml["trade_lane"], orientation="h",
                                marker=dict(color=ml["avg_margin"],
                                            colorscale=[[0,RED],[0.4,YELLOW],[1,GREEN]]),
                                text=[f"{v:.1f}%" for v in ml["avg_margin"]], textposition="auto"))
        fig.add_vline(x=ml["avg_margin"].mean(), line_dash="dash",
                      line_color=YELLOW, annotation_text="Fleet avg")
        fig.update_layout(title="Net Margin % by Trade Lane", **PD, height=380,
                          xaxis_title="Net Margin %")
        st.plotly_chart(fig, use_container_width=True)

    # Freight rate trend
    rate_mo = fv.groupby("month").agg(
        avg_rate=("freight_rate_usd","mean"),
        min_rate=("freight_rate_usd","min"),
        max_rate=("freight_rate_usd","max")
    ).reset_index().sort_values("month")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rate_mo["month"], y=rate_mo["max_rate"], mode="lines",
                             line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=rate_mo["month"], y=rate_mo["min_rate"], mode="lines",
                             fill="tonexty", fillcolor="rgba(14,165,233,0.12)",
                             line=dict(width=0), name="Rate Range"))
    fig.add_trace(go.Scatter(x=rate_mo["month"], y=rate_mo["avg_rate"], mode="lines+markers",
                             line=dict(color=BLUE, width=2.5), name="Avg Freight Rate"))
    fig.update_layout(title="Monthly Freight Rate Trend (USD/TEU)", **PD, height=340,
                      yaxis_title="Freight Rate (USD/TEU)",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        # Cost structure pie
        avg_costs = {"Fuel": fv["fuel_cost_usd"].mean(),
                     "Port Fees": fv["port_cost_usd"].mean(),
                     "Other Opex": (fv["operating_cost_usd"]-fv["fuel_cost_usd"]-fv["port_cost_usd"]).mean()}
        fig = go.Figure(go.Pie(labels=list(avg_costs.keys()),
                                values=list(avg_costs.values()),
                                hole=0.5,
                                marker_colors=[RED, YELLOW, PURPLE],
                                textinfo="label+percent"))
        fig.update_layout(title="Cost Structure (Avg per Voyage)", **PD, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Revenue per TEU by vessel
        fv2 = fv.copy()
        fv2["rev_per_teu"] = fv2["revenue_usd"] / fv2["booked_teu"].replace(0,1)
        rv = fv2.groupby("vessel")["rev_per_teu"].mean().reset_index().sort_values("rev_per_teu")
        fig = go.Figure(go.Bar(x=rv["rev_per_teu"], y=rv["vessel"], orientation="h",
                                marker_color=TEAL,
                                text=[f"${v:.0f}" for v in rv["rev_per_teu"]],
                                textposition="auto"))
        fig.update_layout(title="Avg Revenue per TEU by Vessel", **PD, height=320,
                          xaxis_title="USD per TEU")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4 — VOLUME FORECAST
# ════════════════════════════════════════════════════════════════════
with t4:
    st.markdown('<div class="sec-h">Volume Forecasting & Capacity Planning</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Historical trends, linear projections, and AI-powered 3-month volume forecasts</div>', unsafe_allow_html=True)

    mo_vol = fv.groupby("month").agg(
        teu=("booked_teu","sum"),
        revenue=("revenue_usd","sum"),
        voyages=("voyage_id","count"),
        avg_util=("utilization_pct","mean")
    ).reset_index().sort_values("month")

    # Linear trend projection
    x_idx = np.arange(len(mo_vol))
    slope_teu, intercept_teu, _, _, _ = stats.linregress(x_idx, mo_vol["teu"])
    future_months = pd.period_range(
        pd.Period(mo_vol["month"].iloc[-1], "M") + 1, periods=3, freq="M"
    )
    future_x = np.arange(len(mo_vol), len(mo_vol)+3)
    future_teu = slope_teu * future_x + intercept_teu

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mo_vol["month"], y=mo_vol["teu"], mode="lines+markers",
                             line=dict(color=BLUE, width=2.5), name="Actual TEU"))
    # Trend line
    trend_y = slope_teu * x_idx + intercept_teu
    fig.add_trace(go.Scatter(x=mo_vol["month"], y=trend_y, mode="lines",
                             line=dict(color=YELLOW, width=1.5, dash="dot"), name="Trend"))
    # Forecast
    forecast_x = [mo_vol["month"].iloc[-1]] + [str(m) for m in future_months]
    forecast_y = [mo_vol["teu"].iloc[-1]] + list(future_teu)
    fig.add_trace(go.Scatter(x=forecast_x, y=forecast_y, mode="lines+markers",
                             line=dict(color=GREEN, width=2.5, dash="dash"),
                             marker=dict(symbol="diamond", size=10),
                             name="3-Month Forecast"))
    fig.update_layout(title="TEU Volume: Historical + 3-Month Linear Forecast",
                      **PD, height=380, yaxis_title="TEU Booked",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        # Capacity vs booked
        cap_mo = fv.groupby("month").agg(
            capacity=("capacity_teu","sum"),
            booked=("booked_teu","sum")
        ).reset_index().sort_values("month")
        cap_mo["idle"] = cap_mo["capacity"] - cap_mo["booked"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cap_mo["month"], y=cap_mo["booked"], name="Booked TEU",
                             marker_color=BLUE))
        fig.add_trace(go.Bar(x=cap_mo["month"], y=cap_mo["idle"], name="Idle Capacity",
                             marker_color="#1E2D45"))
        fig.update_layout(title="Capacity Utilisation: Booked vs Idle TEU",
                          barmode="stack", **PD, height=340,
                          yaxis_title="TEU")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Utilisation distribution
        fig = go.Figure()
        for lane in fv["trade_lane"].unique():
            sub = fv[fv["trade_lane"]==lane]["utilization_pct"]
            fig.add_trace(go.Box(y=sub, name=lane.split("–")[1],
                                 marker_color=BLUE, boxmean=True))
        fig.update_layout(title="Utilization Distribution by Destination",
                          **PD, height=340, yaxis_title="Utilization %")
        st.plotly_chart(fig, use_container_width=True)

    # AI Forecast
    st.markdown('<div class="sec-h">🤖 AI Volume Forecast</div>', unsafe_allow_html=True)
    if st.button("Generate AI Volume Forecast", key="fc_ai"):
        with st.spinner("Analysing trends..."):
            monthly_data = mo_vol.tail(12).to_dict("records")
            result = forecast_volumes(monthly_data)
            st.markdown(f'<div class="ai-box">🤖 <strong>AI Forecast Analyst</strong><br><br>{result}</div>',
                        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 5 — CRM PIPELINE
# ════════════════════════════════════════════════════════════════════
with t5:
    st.markdown('<div class="sec-h">CRM Opportunity Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Sales pipeline value, win/loss analysis, rep performance, and opportunity tracking by trade lane</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    pipeline_val = crm[crm["status"]=="In Progress"]["deal_value_usd"].sum()
    won_val = crm[crm["status"]=="Won"]["deal_value_usd"].sum()
    exp_val = crm["expected_value_usd"].sum()
    win_rate = (crm["status"]=="Won").mean()*100
    for col,val,lbl in [
        (c1,f"${pipeline_val/1e6:.1f}M","Pipeline Value"),
        (c2,f"${won_val/1e6:.1f}M","Won Deals"),
        (c3,f"${exp_val/1e6:.1f}M","Expected Value"),
        (c4,f"{win_rate:.1f}%","Win Rate"),
    ]:
        with col:
            st.markdown(f"""<div class="kcard">
                <div class="val">{val}</div><div class="lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        # Funnel
        funnel_order = ["Qualified","Proposal Sent","In Progress","Won","Lost"]
        funnel_df = crm["status"].value_counts().reindex(funnel_order, fill_value=0).reset_index()
        funnel_df.columns = ["stage","count"]
        fig = go.Figure(go.Funnel(
            y=funnel_df["stage"], x=funnel_df["count"],
            marker=dict(color=[GREEN, BLUE, TEAL, YELLOW, RED]),
            textinfo="value+percent total"
        ))
        fig.update_layout(title="CRM Pipeline Funnel", **PD, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Pipeline by trade lane
        pl_lane = crm[crm["status"].isin(["In Progress","Proposal Sent","Qualified"])]\
            .groupby("trade_lane")["deal_value_usd"].sum().reset_index().sort_values("deal_value_usd")
        fig = go.Figure(go.Bar(x=pl_lane["deal_value_usd"]/1e3, y=pl_lane["trade_lane"],
                                orientation="h", marker_color=BLUE,
                                text=[f"${v:.0f}K" for v in pl_lane["deal_value_usd"]/1e3],
                                textposition="auto"))
        fig.update_layout(title="Open Pipeline Value by Trade Lane",
                          **PD, height=360, xaxis_title="Pipeline Value ($K)")
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        # Rep performance
        rep = crm.groupby("sales_rep").agg(
            won=("status", lambda x: (x=="Won").sum()),
            total=("status","count"),
            total_val=("deal_value_usd","sum")
        ).reset_index()
        rep["win_rate"] = rep["won"]/rep["total"]*100
        fig = px.scatter(rep, x="win_rate", y="total_val"/1e3 if False else rep["total_val"]/1e3,
                         size="total", color="win_rate",
                         text="sales_rep",
                         color_continuous_scale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
                         labels={"win_rate":"Win Rate %","y":"Total Deal Value ($K)"},
                         title="Sales Rep: Win Rate vs Deal Value")
        fig.update_traces(textposition="top center")
        fig.update_layout(**PD, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Competitor in lost deals
        lost = crm[crm["status"]=="Lost"]
        comp_lost = lost["competitor"].value_counts().dropna().reset_index()
        comp_lost.columns = ["competitor","lost_to_count"]
        fig = go.Figure(go.Bar(x=comp_lost["competitor"], y=comp_lost["lost_to_count"],
                                marker_color=RED,
                                text=comp_lost["lost_to_count"], textposition="auto"))
        fig.update_layout(title="Deals Lost to Competitors", **PD, height=340,
                          xaxis_title="Competitor", yaxis_title="Lost Deals")
        st.plotly_chart(fig, use_container_width=True)

    # CRM table
    st.markdown('<div class="sec-h">Open Opportunities</div>', unsafe_allow_html=True)
    open_crm = crm[crm["status"].isin(["In Progress","Proposal Sent","Qualified"])]\
        .sort_values("deal_value_usd", ascending=False).head(20)[
            ["opportunity_id","customer","trade_lane","cargo_type",
             "deal_value_usd","status","probability","expected_value_usd","sales_rep"]
        ].copy()
    open_crm["deal_value_usd"] = open_crm["deal_value_usd"].apply(lambda x: f"${x:,.0f}")
    open_crm["expected_value_usd"] = open_crm["expected_value_usd"].apply(lambda x: f"${x:,.0f}")
    open_crm["probability"] = open_crm["probability"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(open_crm, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 6 — MARKET INTELLIGENCE
# ════════════════════════════════════════════════════════════════════
with t6:
    st.markdown('<div class="sec-h">Market Intelligence & Competitor Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Freight rate benchmarking, market share tracking, and competitive positioning across East African trade lanes</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        # Our rate vs competitor avg by lane
        comp_lane = market.groupby("trade_lane").agg(
            our_rate=("our_rate_usd","mean"),
            comp_rate=("competitor_rate_usd","mean"),
            our_share=("our_market_share_pct","mean")
        ).reset_index()
        fig = go.Figure()
        x = comp_lane["trade_lane"]
        fig.add_trace(go.Bar(name="Our Rate", x=x, y=comp_lane["our_rate"], marker_color=BLUE))
        fig.add_trace(go.Bar(name="Competitor Avg", x=x, y=comp_lane["comp_rate"], marker_color=RED))
        fig.update_layout(title="Freight Rate: Ours vs Competitors by Lane",
                          barmode="group", **PD, height=360,
                          yaxis_title="Rate (USD/TEU)")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Market share by lane
        fig = px.bar(comp_lane, x="trade_lane", y="our_share",
                     color="our_share",
                     color_continuous_scale=[[0,RED],[0.4,YELLOW],[1,GREEN]],
                     labels={"our_share":"Market Share %","trade_lane":""},
                     title="Our Market Share % by Trade Lane")
        fig.update_layout(**PD, height=360)
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    # Rate advantage heatmap
    comp_heat = market.groupby(["trade_lane","competitor"])["rate_advantage"].mean().unstack(fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=comp_heat.values, x=comp_heat.columns.tolist(), y=comp_heat.index.tolist(),
        colorscale=[[0,RED],[0.5,"#0A0F1E"],[1,GREEN]],
        text=[[f"${v:+.0f}" for v in row] for row in comp_heat.values],
        texttemplate="%{text}",
        colorbar=dict(title="Rate Advantage\n(USD/TEU)"),
        zmid=0
    ))
    fig.update_layout(title="Rate Advantage vs Each Competitor by Trade Lane (+ve = we are pricier, -ve = we are cheaper)",
                      **PD, height=380)
    st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        # Market share trend
        share_mo = market.groupby("month")["our_market_share_pct"].mean().reset_index().sort_values("month")
        fig = go.Figure(go.Scatter(x=share_mo["month"], y=share_mo["our_market_share_pct"],
                                   mode="lines+markers", fill="tozeroy",
                                   fillcolor="rgba(14,165,233,0.1)",
                                   line=dict(color=BLUE, width=2.5)))
        fig.add_hline(y=share_mo["our_market_share_pct"].mean(), line_dash="dash",
                      line_color=YELLOW, annotation_text="Avg")
        fig.update_layout(title="Market Share % Trend", **PD, height=320,
                          yaxis_title="Market Share %")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Volume by competitor lane
        comp_vol = market.groupby("competitor").agg(
            market_vol=("market_volume_teu","sum"),
            avg_rate=("competitor_rate_usd","mean")
        ).reset_index().sort_values("market_vol", ascending=True)
        fig = go.Figure(go.Bar(x=comp_vol["market_vol"], y=comp_vol["competitor"],
                                orientation="h", marker_color=PURPLE,
                                text=[f"{v:,}" for v in comp_vol["market_vol"]],
                                textposition="auto"))
        fig.update_layout(title="Market Volume (TEU) by Competitor",
                          **PD, height=320, xaxis_title="Market Volume (TEU)")
        st.plotly_chart(fig, use_container_width=True)

    # AI Competitor Intelligence
    st.markdown('<div class="sec-h">🤖 AI Competitive Intelligence Report</div>', unsafe_allow_html=True)
    if st.button("Generate Competitor Intelligence", key="comp_ai"):
        with st.spinner("Analysing market..."):
            mkt_data = comp_lane.round(2).to_dict("records")
            result = competitor_intelligence(mkt_data)
            st.markdown(f'<div class="ai-box">🤖 <strong>Market Intelligence AI</strong><br><br>{result}</div>',
                        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 7 — AI ANALYST
# ════════════════════════════════════════════════════════════════════
with t7:
    st.markdown('<div class="sec-h">🤖 AI Shipping Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-s">Ask anything about the shipping portfolio — voyage performance, cargo mix, revenue, CRM, or market trends.</div>', unsafe_allow_html=True)

    context = {
        "fleet_summary": {
            "total_voyages": len(fv),
            "total_revenue_usd": round(total_rev, 2),
            "avg_utilization_pct": round(avg_util, 2),
            "avg_net_margin_pct": round(avg_margin, 2),
            "total_teu_booked": int(total_teu),
            "avg_freight_rate_usd": round(avg_rate, 2),
            "on_time_pct": round(on_time_pct, 2),
        },
        "top_lane_by_revenue": fv.groupby("trade_lane")["revenue_usd"].sum().idxmax(),
        "lowest_margin_lane": fv.groupby("trade_lane")["net_margin_pct"].mean().idxmin(),
        "crm_pipeline_usd": round(pipeline_val, 2),
        "crm_win_rate_pct": round(win_rate, 2),
        "filters": {"lane": sel_lane, "vessel": sel_vessel, "quarter": sel_q}
    }

    prompts = [
        "Which trade lanes should we prioritise for capacity growth?",
        "What cargo types are most profitable and should we shift our mix?",
        "Where are we losing competitive advantage on freight rates?",
        "How can we improve vessel utilization on underperforming lanes?",
    ]
    st.markdown("**💡 Try asking:**")
    pcols = st.columns(4)
    for i, p in enumerate(prompts):
        with pcols[i]:
            if st.button(p, key=f"p_{i}"):
                st.session_state["ship_q"] = p

    if "ship_msgs" not in st.session_state:
        st.session_state.ship_msgs = []

    for msg in st.session_state.ship_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Ask the AI shipping analyst...")
    if user_q:
        st.session_state.ship_msgs.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("Analysing..."):
                resp = analyze_shipping(user_q, context)
                st.markdown(resp)
                st.session_state.ship_msgs.append({"role": "assistant", "content": resp})