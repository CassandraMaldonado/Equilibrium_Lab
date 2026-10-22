"""Interactive Streamlit decision brief for Equilibrium Lab."""

# I use Streamlit here to turn the experiment results into an interactive
# product decision brief. The calculations stay in the package, while this file
# focuses on helping someone explore the evidence and understand the tradeoffs.

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from equilibrium_lab.analysis import analyze

st.set_page_config(
    page_title="Equilibrium Lab",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#111716; --paper:#f3f0e8; --card:#fbfaf5; --blue:#4666ff; --cyan:#89e4df; --lime:#d7f760; --muted:#68716e; }
    .stApp { background: var(--paper); color: var(--ink); font-family: 'Manrope', sans-serif; }
    [data-testid="stHeader"] { background: rgba(243,240,232,.85); }
    [data-testid="stSidebar"] { background: #111716; }
    [data-testid="stSidebar"] * { color: #f7f7f2 !important; }
    [data-testid="stSidebar"] input { color: #111716 !important; }
    [data-testid="stSidebar"] hr { border-color: #34413d; }
    .block-container { max-width: 1220px; padding-top: 2.5rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.04em; }
    h1 { font-size: clamp(3rem, 7vw, 5.5rem) !important; line-height: .95 !important; margin: .2rem 0 1.25rem !important; }
    h2 { font-size: 2rem !important; }
    .eyebrow { font-family:'DM Mono', monospace; font-size:.68rem; letter-spacing:.13em; color:var(--muted); margin-bottom:.8rem; }
    .hero-copy { max-width: 720px; color: var(--muted); font-size: 1.02rem; line-height:1.7; margin-bottom:2rem; }
    .blue { color:var(--blue); }
    .decision { background:var(--ink); color:white; padding:1.65rem; min-height:255px; box-shadow:12px 12px 0 var(--cyan); }
    .decision small { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.12em; color:#8d9a96; }
    .decision strong { display:block; color:var(--lime); font-size:2.25rem; line-height:1.05; margin:2.1rem 0 .8rem; letter-spacing:-.04em; }
    .decision p { color:#b8c1be; font-size:.82rem; line-height:1.55; }
    .decision .next { border-top:1px solid #34413d; margin-top:1.2rem; padding-top:1rem; color:white; }
    div[data-testid="stMetric"] { background:var(--card); border:1px solid #d7d5cc; padding:1.2rem; min-height:140px; }
    div[data-testid="stMetric"] label { font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.08em; color:var(--muted); }
    div[data-testid="stMetricValue"] { font-weight:700; letter-spacing:-.04em; }
    .section-rule { border-top:1px solid #d7d5cc; margin:2.7rem 0 2rem; }
    .guard { display:grid; grid-template-columns:28px 1fr auto; gap:.7rem; align-items:center; border-top:1px solid #d7d5cc; padding:.9rem 0; }
    .guard i { display:grid; place-items:center; width:21px; height:21px; border-radius:50%; background:#e5f4b8; color:#315c22; font-style:normal; font-size:.7rem; }
    .guard.fail i { background:#fbd5cf; color:#a43b2b; }
    .guard b { font-size:.82rem; }
    .guard span { font-family:'DM Mono',monospace; font-size:.68rem; color:var(--muted); }
    .note { color:var(--muted); font-size:.78rem; line-height:1.6; }
    .access-card { background:var(--card); border:1px solid #d7d5cc; padding:1.2rem; }
    .access-card span { font-family:'DM Mono',monospace; font-size:.62rem; letter-spacing:.08em; color:var(--muted); }
    .access-card b { display:block; font-size:1.75rem; margin-top:.6rem; }
    .stButton > button { width:100%; background:var(--blue); color:white; border:0; border-radius:0; font-weight:700; }
    .stButton > button:hover { background:#314bd1; color:white; border:0; }
    div[data-testid="stDataFrame"] { border:1px solid #d7d5cc; }
    #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def effect_text(value: float, kind: str = "percent") -> str:
    if kind == "percent":
        return f"{value:+.1%}"
    if kind == "money":
        return f"${value:+.2f}"
    return f"{value:+.2f}"


@st.cache_data(show_spinner=False)
def run_analysis(seed: int, zones: int) -> dict:
    return analyze(seed=seed, zones=zones)


with st.sidebar:
    st.markdown("## ⚖️ Equilibrium Lab")
    st.caption("MARKETPLACE EXPERIMENT 029")
    st.divider()
    st.markdown("### Experiment settings")
    seed = st.number_input("Replication seed", min_value=0, max_value=1_000_000, value=29)
    zones = st.slider("Marketplace zones", min_value=8, max_value=40, value=18)
    recompute = st.button("Recompute experiment ↗", type="primary")
    st.divider()
    st.markdown("### Design")
    st.caption("Four-hour switchbacks within geographic zones help reduce interference from a shared supply pool.")
    st.markdown("`28 days`  ·  `hourly panel`")

if recompute:
    run_analysis.clear()

with st.spinner("Estimating marketplace effects…"):
    result = run_analysis(int(seed), int(zones))

hero_left, hero_right = st.columns([1.55, 0.72], gap="large")
with hero_left:
    st.markdown('<p class="eyebrow">MARKETPLACE SCIENCE / SWITCHBACK EXPERIMENT</p>', unsafe_allow_html=True)
    st.markdown("# Better matching.<br><span class='blue'>Balanced outcomes.</span>", unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-copy">I built this experiment to measure whether a matching policy creates value for riders, drivers, and the marketplace—not just one headline metric.</p>',
        unsafe_allow_html=True,
    )
with hero_right:
    st.markdown(
        f"""
        <div class="decision">
          <small>ROLLOUT DECISION</small>
          <strong>{result['decision']['status']}</strong>
          <p>{result['decision']['summary']}</p>
          <p class="next"><small>NEXT MOVE</small><br>{result['decision']['next_action']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric("TRIP CONVERSION", effect_text(result["metrics"]["completion"]["relative_effect"]), "relative effect")
m2.metric("PICKUP TIME", effect_text(result["metrics"]["pickup_minutes"]["effect"], "number"), "minutes")
m3.metric("DRIVER EARNINGS", effect_text(result["metrics"]["driver_earnings"]["effect"], "money"), "per active hour")
m4.metric("CONTRIBUTION", effect_text(result["metrics"]["contribution"]["effect"], "money"), "per zone-hour")

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
st.markdown('<p class="eyebrow">01 / HOURLY EVIDENCE</p>', unsafe_allow_html=True)
st.subheader("The policy performs through the full demand cycle")
hourly = pd.DataFrame(result["hourly"])
figure = go.Figure()
figure.add_trace(go.Scatter(x=hourly["hour"], y=hourly["treatment"], mode="lines", name="Policy", line={"color": "#4666ff", "width": 3}, fill="tonexty", fillcolor="rgba(70,102,255,.09)"))
figure.add_trace(go.Scatter(x=hourly["hour"], y=hourly["control"], mode="lines", name="Control", line={"color": "#9da7a3", "width": 2, "dash": "dash"}))
figure.update_layout(height=380, margin={"l": 10, "r": 10, "t": 30, "b": 10}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", legend={"orientation": "h", "y": 1.1}, xaxis_title="Hour of day", yaxis_title="Completed-trip conversion", yaxis_tickformat=".0%")
figure.update_xaxes(showgrid=False, dtick=2)
figure.update_yaxes(gridcolor="#dedcd4")
st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
left, right = st.columns([1.05, 0.95], gap="large")
with left:
    st.markdown('<p class="eyebrow">02 / MARKET CONDITIONS</p>', unsafe_allow_html=True)
    st.subheader("Where does the policy work best?")
    segment_rows = []
    for name, values in result["demand_segments"].items():
        segment_rows.append({"Market condition": name.title(), "Conversion lift": values["effect"], "Relative lift": values["relative_effect"], "95% CI low": values["ci_low"], "95% CI high": values["ci_high"]})
    segment_frame = pd.DataFrame(segment_rows)
    st.dataframe(segment_frame, use_container_width=True, hide_index=True, column_config={"Conversion lift": st.column_config.NumberColumn(format="%.3f"), "Relative lift": st.column_config.NumberColumn(format="%.1%%"), "95% CI low": st.column_config.NumberColumn(format="%.3f"), "95% CI high": st.column_config.NumberColumn(format="%.3f")})
with right:
    st.markdown('<p class="eyebrow">03 / MARKETPLACE GUARDRAILS</p>', unsafe_allow_html=True)
    st.subheader("Did both sides benefit?")
    for guardrail in result["guardrails"]:
        status = "✓" if guardrail["passed"] else "!"
        css_class = "guard" if guardrail["passed"] else "guard fail"
        st.markdown(f'<div class="{css_class}"><i>{status}</i><b>{guardrail["name"]}</b><span>{guardrail["threshold"]}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
st.markdown('<p class="eyebrow">04 / NEXT ROLLOUT</p>', unsafe_allow_html=True)
st.subheader("Scale where the marketplace can absorb it")
st.markdown('<p class="note">Zones are ranked using expected trip lift, uncertainty, access needs, and current demand pressure. The recommendation keeps active holdouts instead of expanding everywhere at once.</p>', unsafe_allow_html=True)
rollout = pd.DataFrame(result["rollout"])
rollout["zone"] = rollout["zone"].map(lambda value: f"Zone {value + 1:02d}")
rollout["rollout_share"] = rollout["rollout_share"] * 100
rollout["expected_trip_lift"] = rollout["expected_trip_lift"] * 100
st.dataframe(rollout[["zone", "rollout_share", "expected_trip_lift", "demand_pressure", "access_group"]], use_container_width=True, hide_index=True, column_config={"zone": "Zone", "rollout_share": st.column_config.ProgressColumn("Rollout share", format="%.1f%%", min_value=0, max_value=max(rollout["rollout_share"])), "expected_trip_lift": st.column_config.NumberColumn("Expected lift", format="%.2f pp"), "demand_pressure": st.column_config.NumberColumn("Demand pressure", format="%.2fx"), "access_group": "Access group"})

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
st.markdown('<p class="eyebrow">05 / ACCESS CHECK</p>', unsafe_allow_html=True)
st.subheader("Aggregate gains should not hide uneven service")
a1, a2, a3 = st.columns(3)
a1.markdown(f'<div class="access-card"><span>LIMITED-ACCESS EFFECT</span><b>{effect_text(result["access"]["limited_effect"])}</b></div>', unsafe_allow_html=True)
a2.markdown(f'<div class="access-card"><span>STANDARD EFFECT</span><b>{effect_text(result["access"]["standard_effect"])}</b></div>', unsafe_allow_html=True)
a3.markdown(f'<div class="access-card"><span>ACCESS GAP</span><b>{effect_text(result["access"]["gap"])}</b></div>', unsafe_allow_html=True)

with st.expander("How I designed the experiment"):
    st.markdown("""
    - I randomized the policy within four-hour blocks for each geographic zone.
    - I controlled for persistent zone differences and hour-of-day demand patterns.
    - I clustered uncertainty at the zone-by-block level.
    - I required rider, driver, cancellation, and access guardrails to pass before scaling.
    - I kept part of the marketplace in holdout for the phased rollout.
    """)
