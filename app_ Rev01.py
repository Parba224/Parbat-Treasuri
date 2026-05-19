import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config import MIN_CASH_BUFFER, ANNUAL_YIELD
from treasury_engine import calculate_treasury_metrics
from bank_api import normalize_bank_data
from generate_report import generate_treasury_report

from database import (
    init_database,
    create_company,
    get_companies,
    save_analysis,
    get_company_analyses
)

st.set_page_config(page_title="Parbat Treasury", layout="wide")

init_database()

st.markdown("""
<style>
.stApp { background: #f7f9fc; }

.block-container {
    max-width: 1420px;
    padding-top: 1.4rem;
    padding-bottom: 2.5rem;
}

[data-testid="stSidebar"] {
    background: #0b1220;
    width: 225px !important;
}

[data-testid="stSidebar"] * { color: #f8fafc; }

.logo-box {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 26px;
}

.logo-mark {
    width: 38px;
    height: 38px;
    background: #2563eb;
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 22px;
    margin-bottom: 12px;
}

.logo-title {
    font-size: 22px;
    font-weight: 850;
    color: white;
}

.logo-sub {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 6px;
}

.hero, .panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
    margin-top: 20px;
}

.hero-title {
    font-size: 34px;
    font-weight: 900;
    color: #0f172a;
}

.hero-subtitle, .panel-subtitle {
    font-size: 14px;
    color: #64748b;
    margin-top: 6px;
    margin-bottom: 14px;
}

.kpi-card {
    background: #0f172a;
    border-radius: 22px;
    padding: 26px;
    min-height: 150px;
    box-shadow: 0 14px 28px rgba(15, 23, 42, 0.13);
}

.kpi-label, .status-label {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 14px;
}

.kpi-value {
    color: white;
    font-size: 36px;
    font-weight: 900;
}

.kpi-sub {
    color: #60a5fa;
    font-size: 13px;
    margin-top: 14px;
}

.status-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 24px;
    min-height: 128px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
}

.status-value {
    color: #0f172a;
    font-size: 30px;
    font-weight: 900;
}

.status-sub {
    color: #64748b;
    font-size: 13px;
    margin-top: 8px;
}

.panel-title {
    font-size: 22px;
    font-weight: 850;
    color: #0f172a;
}

.health-badge, .moderate-badge, .critical-badge {
    display: inline-block;
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 800;
    margin-top: 14px;
}

.health-badge {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
}

.moderate-badge {
    background: #fef9c3;
    color: #854d0e;
    border: 1px solid #fde047;
}

.critical-badge {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.insight {
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
    border-left: 6px solid #22c55e;
    border-radius: 18px;
    padding: 20px;
    color: #064e3b;
    font-size: 16px;
    line-height: 1.55;
}

.warning {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 6px solid #f97316;
    border-radius: 18px;
    padding: 20px;
    color: #7c2d12;
    font-size: 16px;
    line-height: 1.55;
}
            
[data-testid="stSidebar"] input {
    color: #0f172a !important;
    background-color: #ffffff !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: #64748b !important;
}

[data-testid="stSidebar"] .stNumberInput button {
    background-color: #ef4444 !important;
    color: white !important;
}

[data-testid="stSidebar"] select {
    color: #0f172a !important;
    background-color: #ffffff !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #0f172a !important;
}            

</style>
""", unsafe_allow_html=True)

# SIDEBAR — UPLOAD

uploaded_file = st.sidebar.file_uploader(
    "Upload Bank CSV",
    type=["csv"]
)

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    df = normalize_bank_data(raw_df)
else:
    raw_df = pd.read_csv("data/demo_transactions.csv")
    df = normalize_bank_data(raw_df)

# SIDEBAR — BRAND

st.sidebar.markdown("""
<div class="logo-box">
    <div class="logo-mark">P</div>
    <div class="logo-title">Parbat</div>
    <div class="logo-sub">Treasury intelligence</div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR — COMPANY

st.sidebar.divider()

st.sidebar.markdown("### Company")

company_name = st.sidebar.text_input(
    "Company name",
    value="Demo Company"
)

if st.sidebar.button("Create Company"):
    create_company(company_name)
    st.sidebar.success("Company created")

companies = get_companies()

company_options = {
    f"{name} — ID {company_id}": company_id
    for company_id, name in companies
}

selected_company_id = None

if company_options:
    selected_company_label = st.sidebar.selectbox(
        "Select company",
        list(company_options.keys())
    )

    selected_company_id = company_options[selected_company_label]

# LANGUAGE

language = st.sidebar.radio(
    "Language / Idioma",
    ["English", "Español"],
    index=0
)

TEXTS = {

    "English": {

        "hero_title": "Parbat Treasury",
        "hero_subtitle": "Liquidity intelligence, cash efficiency analysis and yield simulation for companies.",
        "save_analysis": "Save Analysis",
        "save_analysis_sub": "Store this treasury analysis under the selected company.",
        "save_button": "Save Current Analysis",
        "treasury_report": "Treasury Report",
        "generate_pdf": "Generate Treasury PDF Report",
        "ai_recommendations": "AI Treasury Recommendations",
        "transactions": "Transactions",
        "company_history": "Company Analysis History"

    },

    "Español": {

        "hero_title": "Parbat Treasury",
        "hero_subtitle": "Inteligencia de liquidez, eficiencia de caja y simulación de rentabilidad para empresas.",
        "save_analysis": "Guardar análisis",
        "save_analysis_sub": "Guardar este análisis financiero para la empresa seleccionada.",
        "save_button": "Guardar análisis actual",
        "treasury_report": "Informe Treasury",
        "generate_pdf": "Generar informe PDF",
        "ai_recommendations": "Recomendaciones IA Treasury",
        "transactions": "Transacciones",
        "company_history": "Historial de análisis"

    }

}

T = TEXTS[language]

# SIDEBAR — SETTINGS

st.sidebar.divider()

min_cash_buffer = st.sidebar.number_input(
    "Minimum Cash Buffer (€)",
    min_value=0,
    value=MIN_CASH_BUFFER,
    step=1000
)

annual_yield = st.sidebar.slider(
    "Estimated Annual Yield",
    min_value=0.00,
    max_value=0.10,
    value=ANNUAL_YIELD,
    step=0.005,
    format="%.3f"
)

# ENGINE

metrics = calculate_treasury_metrics(
    df,
    min_cash_buffer,
    annual_yield
)

idle_cash_ratio = metrics["idle_cash_ratio"]
treasury_score = metrics["treasury_score"]

if treasury_score >= 75:
    liquidity_status = "HEALTHY"
    badge_class = "health-badge"
elif treasury_score >= 50:
    liquidity_status = "MODERATE"
    badge_class = "moderate-badge"
else:
    liquidity_status = "CRITICAL"
    badge_class = "critical-badge"

# HERO

st.markdown(f"""
<div class="hero">
    <div class="hero-title">Parbat Treasury</div>
    <div class="hero-subtitle">
        Liquidity intelligence, cash efficiency analysis and yield simulation for companies.
    </div>
    <div class="{badge_class}">
        Liquidity Status: {liquidity_status}
    </div>
</div>
""", unsafe_allow_html=True)

# MAIN KPI CARDS

col1, col2, col3, col4 = st.columns(4)

cards = [
    ("Current Cash", metrics["current_balance"], "Available company liquidity"),
    ("Protected Buffer", metrics["min_cash_buffer"], "Minimum operating reserve"),
    ("Excess Liquidity", metrics["excess_cash"], "Cash above protected buffer"),
    ("Annual Potential", metrics["annual_potential_return"], "Estimated yearly opportunity"),
]

for col, (label, value, sub) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">€{value:,.0f}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

# SECONDARY KPI CARDS

col5, col6, col7, col8 = st.columns(4)

secondary = [
    ("Treasury Score", f"{treasury_score}/100", "Liquidity efficiency score"),
    ("Idle Cash Ratio", f"{idle_cash_ratio*100:.1f}%", "Share of cash above buffer"),
    ("Monthly Burn", f"€{metrics['monthly_burn']:,.0f}", "Detected monthly expenses"),
    ("Net Cashflow", f"€{metrics['net_cashflow']:,.0f}", "Net liquidity movement"),
]

for col, (label, value, sub) in zip([col5, col6, col7, col8], secondary):
    with col:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-label">{label}</div>
            <div class="status-value">{value}</div>
            <div class="status-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

col9, col10 = st.columns(2)

with col9:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Monthly Income</div>
        <div class="status-value">€{metrics['monthly_income']:,.0f}</div>
        <div class="status-sub">Detected incoming cashflow</div>
    </div>
    """, unsafe_allow_html=True)

with col10:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Runway Estimate</div>
        <div class="status-value">{metrics['runway_months']:.1f} months</div>
        <div class="status-sub">Estimated liquidity runway</div>
    </div>
    """, unsafe_allow_html=True)

# LIQUIDITY OVERVIEW

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Liquidity Overview</div>
    <div class="panel-subtitle">
        Daily cash balance from uploaded banking data.
    </div>
</div>
""", unsafe_allow_html=True)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["balance"],
    mode="lines+markers",
    line=dict(width=3, color="#2563eb"),
    marker=dict(size=7, color="#2563eb"),
    name="Balance"
))

fig.add_trace(go.Scatter(
    x=df["date"],
    y=[min_cash_buffer] * len(df),
    mode="lines",
    line=dict(width=2, color="#ef4444", dash="dash"),
    name="Cash buffer"
))

fig.update_layout(
    height=345,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#0f172a", size=13),
    xaxis=dict(gridcolor="#f1f5f9"),
    yaxis=dict(gridcolor="#f1f5f9"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# EXPENSE BREAKDOWN

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Expense Breakdown</div>
    <div class="panel-subtitle">
        Automatic categorization of company expenses.
    </div>
</div>
""", unsafe_allow_html=True)

expense_summary = metrics["expense_summary"]

fig_expenses = px.pie(
    expense_summary,
    names="category",
    values="total",
    hole=0.6
)

fig_expenses.update_layout(
    height=420,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#0f172a")
)

st.plotly_chart(fig_expenses, use_container_width=True)

st.dataframe(
    expense_summary,
    use_container_width=True,
    hide_index=True
)

# RECURRING EXPENSES

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Recurring Expenses</div>
    <div class="panel-subtitle">
        Detected repeated obligations based on transaction patterns.
    </div>
</div>
""", unsafe_allow_html=True)

recurring_expenses = metrics["recurring_expenses"]

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Recurring Monthly Obligations</div>
        <div class="status-value">€{metrics['recurring_monthly_total']:,.0f}</div>
        <div class="status-sub">Estimated repeated monthly costs</div>
    </div>
    """, unsafe_allow_html=True)

with col_r2:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Fixed Cost Ratio</div>
        <div class="status-value">{metrics['fixed_cost_ratio']*100:.1f}%</div>
        <div class="status-sub">Recurring costs as share of burn</div>
    </div>
    """, unsafe_allow_html=True)

if recurring_expenses.empty:
    st.info("No recurring expenses detected yet.")
else:
    st.dataframe(
        recurring_expenses,
        use_container_width=True,
        hide_index=True
    )

# FORECAST ENGINE

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Cash Forecast</div>
    <div class="panel-subtitle">
        30-day projected liquidity based on income and recurring obligations.
    </div>
</div>
""", unsafe_allow_html=True)

forecast_df = metrics["forecast_df"]
risk_alert = metrics["risk_alert"]
recommendation = metrics["recommendation"]

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Projected 30-Day Balance</div>
        <div class="status-value">€{metrics['projected_30_day_balance']:,.0f}</div>
        <div class="status-sub">Forecasted liquidity position</div>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Suggested Deployable Cash</div>
        <div class="status-value">€{recommendation['suggested_deployable_cash']:,.0f}</div>
        <div class="status-sub">After conservative reserve</div>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Risk Level</div>
        <div class="status-value">{risk_alert['risk_level']}</div>
        <div class="status-sub">{risk_alert['message']}</div>
    </div>
    """, unsafe_allow_html=True)

fig_forecast = go.Figure()

fig_forecast.add_trace(go.Scatter(
    x=forecast_df["day"],
    y=forecast_df["projected_balance"],
    mode="lines",
    line=dict(width=3, color="#16a34a"),
    name="Projected balance"
))

fig_forecast.add_trace(go.Scatter(
    x=forecast_df["day"],
    y=[min_cash_buffer] * len(forecast_df),
    mode="lines",
    line=dict(width=2, color="#ef4444", dash="dash"),
    name="Cash buffer"
))

fig_forecast.update_layout(
    height=340,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#0f172a", size=13),
    xaxis=dict(gridcolor="#f1f5f9", title="Days"),
    yaxis=dict(gridcolor="#f1f5f9", title="Projected cash balance (€)"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig_forecast, use_container_width=True)

# TREASURY INSIGHT

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Treasury Insight</div>
    <div class="panel-subtitle">
        Automated interpretation of the company liquidity position.
    </div>
</div>
""", unsafe_allow_html=True)

if metrics["excess_cash"] > 0:
    st.markdown(f"""
    <div class="insight">
        <b>{liquidity_status} liquidity profile.</b><br><br>
        The company holds <b>€{metrics['excess_cash']:,.0f}</b> above its protected operating buffer.
        At an estimated annual yield of <b>{metrics['annual_yield']*100:.2f}%</b>,
        this could generate approximately <b>€{metrics['annual_potential_return']:,.0f}</b> per year.
        <br><br>
        Treasury Score: <b>{treasury_score}/100</b>.
        Idle Cash Ratio: <b>{idle_cash_ratio*100:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="warning">
        <b>No excess liquidity detected.</b><br><br>
        Current cash remains within the selected protected operating buffer.
    </div>
    """, unsafe_allow_html=True)

st.write("TEST AI BLOCK")    

# AI TREASURY RECOMMENDATIONS

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["ai_recommendations"]}</div>
    <div class="panel-subtitle">
        Automated treasury optimization recommendations generated from company liquidity data.
    </div>
</div>
""", unsafe_allow_html=True)

recommendations = []

# LIQUIDITY

if metrics["excess_cash"] > 20000:
    recommendations.append(
        f"Idle liquidity remains elevated. Consider deploying approximately "
        f"€{metrics['excess_cash']:,.0f} into short-duration yield products "
        f"while maintaining the protected operating reserve."
    )

# RUNWAY

if metrics["runway_months"] < 3:
    recommendations.append(
        "Liquidity runway is below 3 months. Reducing fixed costs or "
        "increasing retained cash reserves is recommended."
    )
elif metrics["runway_months"] > 12:
    recommendations.append(
        "The company maintains a very conservative liquidity position. "
        "Treasury capital efficiency could potentially be improved."
    )

# FIXED COSTS

if metrics["fixed_cost_ratio"] > 0.60:
    recommendations.append(
        "Recurring obligations represent a high percentage of monthly burn. "
        "Monitoring fixed operational commitments is recommended."
    )

# TREASURY SCORE

if treasury_score >= 80:
    recommendations.append(
        "Treasury structure appears strong with healthy liquidity management "
        "and stable operational coverage."
    )

elif treasury_score < 50:
    recommendations.append(
        "Treasury efficiency appears weak relative to current burn and liquidity structure."
    )

# DEPLOYABLE CASH

if metrics["recommendation"]["suggested_deployable_cash"] > 10000:
    recommendations.append(
        f"An estimated €{metrics['recommendation']['suggested_deployable_cash']:,.0f} "
        f"could potentially be allocated into low-risk treasury products "
        f"without compromising short-term liquidity."
    )

# OUTPUT

if recommendations:

    for rec in recommendations:

        st.markdown(f"""
        <div class="insight">
            {rec}
        </div>
        """, unsafe_allow_html=True)

else:

    st.markdown(f"""
    <div class="warning">
        No significant treasury optimization opportunities detected at the current liquidity profile.
    </div>
    """, unsafe_allow_html=True)    

# SAVE ANALYSIS

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["save_analysis"]}</div>
    <div class="panel-subtitle">
    {T["save_analysis_sub"]}
</div>
""", unsafe_allow_html=True)

if selected_company_id is not None:
    if st.button(T["save_button"]):
        save_analysis(selected_company_id, metrics)
        st.success("Analysis saved successfully.")
else:
    st.warning("Create or select a company before saving this analysis.")

# TREASURY REPORT

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["treasury_report"]}</div>
    <div class="panel-subtitle">
        Generate a professional PDF treasury report.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Generate Treasury PDF Report"):
    pdf_path = generate_treasury_report(metrics)

    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="Download Treasury Report",
            data=pdf_file,
            file_name="parbat_treasury_report.pdf",
            mime="application/pdf"
        )

# COMPANY HISTORY

if selected_company_id is not None:
    analyses = get_company_analyses(selected_company_id)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["company_history"]}</div>
        <div class="panel-subtitle">
            Previous saved treasury analyses for this company.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if analyses:
        history_df = pd.DataFrame(
            analyses,
            columns=[
                "created_at",
                "current_cash",
                "excess_liquidity",
                "treasury_score",
                "projected_30_day_balance",
                "suggested_deployable_cash"
            ]
        )

        history_df["created_at"] = pd.to_datetime(
            history_df["created_at"]
        )

        history_df = history_df.sort_values("created_at")

        col_h1, col_h2 = st.columns(2)

        with col_h1:
            fig_cash_history = go.Figure()

            fig_cash_history.add_trace(go.Scatter(
                x=history_df["created_at"],
                y=history_df["current_cash"],
                mode="lines+markers",
                line=dict(width=3, color="#2563eb"),
                marker=dict(size=7),
                name="Current cash"
            ))

            fig_cash_history.update_layout(
                height=320,
                title="Current Cash History",
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#0f172a", size=13),
                xaxis=dict(gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9")
            )

            st.plotly_chart(
                fig_cash_history,
                use_container_width=True
            )

        with col_h2:
            fig_score_history = go.Figure()

            fig_score_history.add_trace(go.Scatter(
                x=history_df["created_at"],
                y=history_df["treasury_score"],
                mode="lines+markers",
                line=dict(width=3, color="#16a34a"),
                marker=dict(size=7),
                name="Treasury score"
            ))

            fig_score_history.update_layout(
                height=320,
                title="Treasury Score History",
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#0f172a", size=13),
                xaxis=dict(gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9")
            )

            st.plotly_chart(
                fig_score_history,
                use_container_width=True
            )

        col_h3, col_h4 = st.columns(2)

        with col_h3:
            fig_excess_history = go.Figure()

            fig_excess_history.add_trace(go.Scatter(
                x=history_df["created_at"],
                y=history_df["excess_liquidity"],
                mode="lines+markers",
                line=dict(width=3, color="#9333ea"),
                marker=dict(size=7),
                name="Excess liquidity"
            ))

            fig_excess_history.update_layout(
                height=320,
                title="Excess Liquidity History",
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#0f172a", size=13),
                xaxis=dict(gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9")
            )

            st.plotly_chart(
                fig_excess_history,
                use_container_width=True
            )

        with col_h4:
            fig_deployable_history = go.Figure()

            fig_deployable_history.add_trace(go.Scatter(
                x=history_df["created_at"],
                y=history_df["suggested_deployable_cash"],
                mode="lines+markers",
                line=dict(width=3, color="#f97316"),
                marker=dict(size=7),
                name="Deployable cash"
            ))

            fig_deployable_history.update_layout(
                height=320,
                title="Suggested Deployable Cash History",
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#0f172a", size=13),
                xaxis=dict(gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9")
            )

            st.plotly_chart(
                fig_deployable_history,
                use_container_width=True
            )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No saved analyses for this company yet.")

# TRANSACTIONS

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["transactions"]}</div>
    <div class="panel-subtitle">
        Imported banking transactions used for this analysis.
    </div>
</div>
""", unsafe_allow_html=True)

st.dataframe(
    metrics["df"],
    use_container_width=True,
    hide_index=True
)