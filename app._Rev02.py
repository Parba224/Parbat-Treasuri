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

TEXTS = {
    "English": {
        "upload": "Upload Bank CSV",
        "company": "Company",
        "company_name": "Company name",
        "create_company": "Create Company",
        "company_created": "Company created",
        "select_company": "Select company",
        "min_cash_buffer": "Minimum Cash Buffer (€)",
        "annual_yield": "Estimated Annual Yield",

        "hero_title": "Parbat Treasury",
        "hero_subtitle": "Liquidity intelligence, cash efficiency analysis and yield simulation for companies.",
        "liquidity_status": "Liquidity Status",

        "current_cash": "Current Cash",
        "current_cash_sub": "Available company liquidity",
        "protected_buffer": "Protected Buffer",
        "protected_buffer_sub": "Minimum operating reserve",
        "excess_liquidity": "Excess Liquidity",
        "excess_liquidity_sub": "Cash above protected buffer",
        "annual_potential": "Annual Potential",
        "annual_potential_sub": "Estimated yearly opportunity",

        "treasury_score": "Treasury Score",
        "treasury_score_sub": "Liquidity efficiency score",
        "idle_cash_ratio": "Idle Cash Ratio",
        "idle_cash_ratio_sub": "Share of cash above buffer",
        "monthly_burn": "Monthly Burn",
        "monthly_burn_sub": "Detected monthly expenses",
        "net_cashflow": "Net Cashflow",
        "net_cashflow_sub": "Net liquidity movement",
        "monthly_income": "Monthly Income",
        "monthly_income_sub": "Detected incoming cashflow",
        "runway": "Runway Estimate",
        "runway_sub": "Estimated liquidity runway",

        "liquidity_overview": "Liquidity Overview",
        "liquidity_overview_sub": "Daily cash balance from uploaded banking data.",
        "expense_breakdown": "Expense Breakdown",
        "expense_breakdown_sub": "Automatic categorization of company expenses.",
        "recurring_expenses": "Recurring Expenses",
        "recurring_expenses_sub": "Detected repeated obligations based on transaction patterns.",
        "recurring_monthly": "Recurring Monthly Obligations",
        "recurring_monthly_sub": "Estimated repeated monthly costs",
        "fixed_cost_ratio": "Fixed Cost Ratio",
        "fixed_cost_ratio_sub": "Recurring costs as share of burn",
        "no_recurring": "No recurring expenses detected yet.",

        "cash_forecast": "Cash Forecast",
        "cash_forecast_sub": "30-day projected liquidity based on income and recurring obligations.",
        "projected_balance": "Projected 30-Day Balance",
        "projected_balance_sub": "Forecasted liquidity position",
        "deployable_cash": "Suggested Deployable Cash",
        "deployable_cash_sub": "After conservative reserve",
        "risk_level": "Risk Level",

        "treasury_insight": "Treasury Insight",
        "treasury_insight_sub": "Automated interpretation of the company liquidity position.",
        "no_excess": "No excess liquidity detected.",
        "no_excess_sub": "Current cash remains within the selected protected operating buffer.",

        "ai_recommendations": "AI Treasury Recommendations",
        "ai_recommendations_sub": "Automated treasury optimization recommendations generated from company liquidity data.",
        "no_ai": "No significant treasury optimization opportunities detected at the current liquidity profile.",

        "save_analysis": "Save Analysis",
        "save_analysis_sub": "Store this treasury analysis under the selected company.",
        "save_button": "Save Current Analysis",
        "saved_ok": "Analysis saved successfully.",
        "save_warning": "Create or select a company before saving this analysis.",

        "treasury_report": "Treasury Report",
        "treasury_report_sub": "Generate a professional PDF treasury report.",
        "generate_pdf": "Generate Treasury PDF Report",
        "download_pdf": "Download Treasury Report",

        "company_history": "Company Analysis History",
        "company_history_sub": "Previous saved treasury analyses for this company.",
        "no_history": "No saved analyses for this company yet.",

        "transactions": "Transactions",
        "transactions_sub": "Imported banking transactions used for this analysis.",

        "healthy_profile": "liquidity profile.",
        "company_holds": "The company holds",
        "above_buffer": "above its protected operating buffer.",
        "yield_text": "At an estimated annual yield of",
        "could_generate": "this could generate approximately",
        "per_year": "per year.",
    },

    "Español": {
        "upload": "Subir CSV bancario",
        "company": "Empresa",
        "company_name": "Nombre de empresa",
        "create_company": "Crear empresa",
        "company_created": "Empresa creada",
        "select_company": "Seleccionar empresa",
        "min_cash_buffer": "Colchón mínimo de caja (€)",
        "annual_yield": "Rentabilidad anual estimada",

        "hero_title": "Parbat Treasury",
        "hero_subtitle": "Inteligencia de liquidez, eficiencia de caja y simulación de rentabilidad para empresas.",
        "liquidity_status": "Estado de liquidez",

        "current_cash": "Caja actual",
        "current_cash_sub": "Liquidez disponible de la empresa",
        "protected_buffer": "Colchón protegido",
        "protected_buffer_sub": "Reserva operativa mínima",
        "excess_liquidity": "Liquidez excedente",
        "excess_liquidity_sub": "Caja por encima del colchón",
        "annual_potential": "Potencial anual",
        "annual_potential_sub": "Oportunidad anual estimada",

        "treasury_score": "Puntuación Treasury",
        "treasury_score_sub": "Puntuación de eficiencia de liquidez",
        "idle_cash_ratio": "Ratio de caja parada",
        "idle_cash_ratio_sub": "Porcentaje de caja sobre el colchón",
        "monthly_burn": "Gasto mensual",
        "monthly_burn_sub": "Gastos mensuales detectados",
        "net_cashflow": "Flujo neto de caja",
        "net_cashflow_sub": "Movimiento neto de liquidez",
        "monthly_income": "Ingresos mensuales",
        "monthly_income_sub": "Entradas de caja detectadas",
        "runway": "Runway estimado",
        "runway_sub": "Meses estimados de liquidez",

        "liquidity_overview": "Resumen de liquidez",
        "liquidity_overview_sub": "Balance diario de caja según los datos bancarios cargados.",
        "expense_breakdown": "Desglose de gastos",
        "expense_breakdown_sub": "Categorización automática de gastos de la empresa.",
        "recurring_expenses": "Gastos recurrentes",
        "recurring_expenses_sub": "Obligaciones repetidas detectadas por patrones de transacciones.",
        "recurring_monthly": "Obligaciones recurrentes mensuales",
        "recurring_monthly_sub": "Costes mensuales repetidos estimados",
        "fixed_cost_ratio": "Ratio de costes fijos",
        "fixed_cost_ratio_sub": "Costes recurrentes sobre gasto mensual",
        "no_recurring": "Todavía no se han detectado gastos recurrentes.",

        "cash_forecast": "Previsión de caja",
        "cash_forecast_sub": "Proyección de liquidez a 30 días basada en ingresos y obligaciones recurrentes.",
        "projected_balance": "Balance proyectado a 30 días",
        "projected_balance_sub": "Posición de liquidez prevista",
        "deployable_cash": "Caja desplegable sugerida",
        "deployable_cash_sub": "Después de la reserva conservadora",
        "risk_level": "Nivel de riesgo",

        "treasury_insight": "Insight Treasury",
        "treasury_insight_sub": "Interpretación automática de la posición de liquidez de la empresa.",
        "no_excess": "No se detecta liquidez excedente.",
        "no_excess_sub": "La caja actual se mantiene dentro del colchón operativo protegido.",

        "ai_recommendations": "Recomendaciones IA Treasury",
        "ai_recommendations_sub": "Recomendaciones automáticas de optimización treasury generadas desde los datos de liquidez.",
        "no_ai": "No se detectan oportunidades significativas de optimización treasury con el perfil actual.",

        "save_analysis": "Guardar análisis",
        "save_analysis_sub": "Guardar este análisis treasury bajo la empresa seleccionada.",
        "save_button": "Guardar análisis actual",
        "saved_ok": "Análisis guardado correctamente.",
        "save_warning": "Crea o selecciona una empresa antes de guardar este análisis.",

        "treasury_report": "Informe Treasury",
        "treasury_report_sub": "Generar un informe PDF profesional de treasury.",
        "generate_pdf": "Generar informe PDF",
        "download_pdf": "Descargar informe Treasury",

        "company_history": "Historial de análisis de empresa",
        "company_history_sub": "Análisis treasury guardados previamente para esta empresa.",
        "no_history": "Todavía no hay análisis guardados para esta empresa.",

        "transactions": "Transacciones",
        "transactions_sub": "Transacciones bancarias importadas usadas para este análisis.",

        "healthy_profile": "perfil de liquidez.",
        "company_holds": "La empresa mantiene",
        "above_buffer": "por encima de su colchón operativo protegido.",
        "yield_text": "Con una rentabilidad anual estimada de",
        "could_generate": "esto podría generar aproximadamente",
        "per_year": "al año.",
    }
}

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
</style>
""", unsafe_allow_html=True)

language = st.sidebar.radio(
    "Language / Idioma",
    ["English", "Español"],
    index=0
)

T = TEXTS[language]

uploaded_file = st.sidebar.file_uploader(T["upload"], type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    df = normalize_bank_data(raw_df)
else:
    raw_df = pd.read_csv("data/demo_transactions.csv")
    df = normalize_bank_data(raw_df)

st.sidebar.markdown("""
<div class="logo-box">
    <div class="logo-mark">P</div>
    <div class="logo-title">Parbat</div>
    <div class="logo-sub">Treasury intelligence</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown(f"### {T['company']}")

company_name = st.sidebar.text_input(
    T["company_name"],
    value="Demo Company"
)

if st.sidebar.button(T["create_company"]):
    create_company(company_name)
    st.sidebar.success(T["company_created"])

companies = get_companies()

company_options = {
    f"{name} — ID {company_id}": company_id
    for company_id, name in companies
}

selected_company_id = None

if company_options:
    selected_company_label = st.sidebar.selectbox(
        T["select_company"],
        list(company_options.keys())
    )
    selected_company_id = company_options[selected_company_label]

st.sidebar.divider()

min_cash_buffer = st.sidebar.number_input(
    T["min_cash_buffer"],
    min_value=0,
    value=MIN_CASH_BUFFER,
    step=1000
)

annual_yield = st.sidebar.slider(
    T["annual_yield"],
    min_value=0.00,
    max_value=0.10,
    value=ANNUAL_YIELD,
    step=0.005,
    format="%.3f"
)

metrics = calculate_treasury_metrics(df, min_cash_buffer, annual_yield)

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

# EXECUTIVE MODE

st.markdown(f"""
<div class="panel">
    <div class="panel-title">Executive Mode</div>
    <div class="panel-subtitle">
        CFO-level summary of liquidity health, runway and deployable treasury capital.
    </div>
</div>
""", unsafe_allow_html=True)

risk_score = 100

if metrics["runway_months"] < 3:
    risk_score -= 35

if metrics["fixed_cost_ratio"] > 0.60:
    risk_score -= 25

if metrics["excess_cash"] <= 0:
    risk_score -= 30

risk_score = max(0, min(100, risk_score))

deployable_ratio = (
    metrics["recommendation"]["suggested_deployable_cash"] / metrics["current_balance"]
    if metrics["current_balance"] > 0
    else 0
)

runway_score = min(100, metrics["runway_months"] / 12 * 100)

col_exec1, col_exec2, col_exec3, col_exec4 = st.columns(4)

with col_exec1:
    fig_score = go.Figure(go.Indicator(
        mode="gauge+number",
        value=treasury_score,
        title={"text": "Treasury Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2563eb"},
            "steps": [
                {"range": [0, 50], "color": "#fee2e2"},
                {"range": [50, 75], "color": "#fef9c3"},
                {"range": [75, 100], "color": "#dcfce7"},
            ],
        }
    ))

    fig_score.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        font=dict(color="#0f172a")
    )

    st.plotly_chart(fig_score, use_container_width=True)

with col_exec2:
    fig_risk = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": "Liquidity Risk Control"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#16a34a"},
            "steps": [
                {"range": [0, 50], "color": "#fee2e2"},
                {"range": [50, 75], "color": "#fef9c3"},
                {"range": [75, 100], "color": "#dcfce7"},
            ],
        }
    ))

    fig_risk.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        font=dict(color="#0f172a")
    )

    st.plotly_chart(fig_risk, use_container_width=True)

with col_exec3:
    fig_runway = go.Figure(go.Indicator(
        mode="gauge+number",
        value=runway_score,
        title={"text": "Runway Strength"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#9333ea"},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        }
    ))

    fig_runway.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        font=dict(color="#0f172a")
    )

    st.plotly_chart(fig_runway, use_container_width=True)

with col_exec4:
    fig_deployable = go.Figure(go.Indicator(
        mode="gauge+number",
        value=deployable_ratio * 100,
        title={"text": "Deployable Cash Ratio"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#f97316"},
            "steps": [
                {"range": [0, 25], "color": "#e2e8f0"},
                {"range": [25, 50], "color": "#dbeafe"},
                {"range": [50, 100], "color": "#dcfce7"},
            ],
        }
    ))

    fig_deployable.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        font=dict(color="#0f172a")
    )

    st.plotly_chart(fig_deployable, use_container_width=True)    

st.markdown(f"""
<div class="hero">
    <div class="hero-title">{T["hero_title"]}</div>
    <div class="hero-subtitle">{T["hero_subtitle"]}</div>
    <div class="{badge_class}">
        {T["liquidity_status"]}: {liquidity_status}
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

cards = [
    (T["current_cash"], metrics["current_balance"], T["current_cash_sub"]),
    (T["protected_buffer"], metrics["min_cash_buffer"], T["protected_buffer_sub"]),
    (T["excess_liquidity"], metrics["excess_cash"], T["excess_liquidity_sub"]),
    (T["annual_potential"], metrics["annual_potential_return"], T["annual_potential_sub"]),
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

col5, col6, col7, col8 = st.columns(4)

secondary = [
    (T["treasury_score"], f"{treasury_score}/100", T["treasury_score_sub"]),
    (T["idle_cash_ratio"], f"{idle_cash_ratio*100:.1f}%", T["idle_cash_ratio_sub"]),
    (T["monthly_burn"], f"€{metrics['monthly_burn']:,.0f}", T["monthly_burn_sub"]),
    (T["net_cashflow"], f"€{metrics['net_cashflow']:,.0f}", T["net_cashflow_sub"]),
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
        <div class="status-label">{T["monthly_income"]}</div>
        <div class="status-value">€{metrics['monthly_income']:,.0f}</div>
        <div class="status-sub">{T["monthly_income_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

with col10:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["runway"]}</div>
        <div class="status-value">{metrics['runway_months']:.1f} months</div>
        <div class="status-sub">{T["runway_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["liquidity_overview"]}</div>
    <div class="panel-subtitle">{T["liquidity_overview_sub"]}</div>
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
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["expense_breakdown"]}</div>
    <div class="panel-subtitle">{T["expense_breakdown_sub"]}</div>
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

st.dataframe(expense_summary, use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["recurring_expenses"]}</div>
    <div class="panel-subtitle">{T["recurring_expenses_sub"]}</div>
</div>
""", unsafe_allow_html=True)

recurring_expenses = metrics["recurring_expenses"]

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["recurring_monthly"]}</div>
        <div class="status-value">€{metrics['recurring_monthly_total']:,.0f}</div>
        <div class="status-sub">{T["recurring_monthly_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

with col_r2:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["fixed_cost_ratio"]}</div>
        <div class="status-value">{metrics['fixed_cost_ratio']*100:.1f}%</div>
        <div class="status-sub">{T["fixed_cost_ratio_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

if recurring_expenses.empty:
    st.info(T["no_recurring"])
else:
    st.dataframe(recurring_expenses, use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["cash_forecast"]}</div>
    <div class="panel-subtitle">{T["cash_forecast_sub"]}</div>
</div>
""", unsafe_allow_html=True)

forecast_df = metrics["forecast_df"]
risk_alert = metrics["risk_alert"]
recommendation = metrics["recommendation"]

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["projected_balance"]}</div>
        <div class="status-value">€{metrics['projected_30_day_balance']:,.0f}</div>
        <div class="status-sub">{T["projected_balance_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["deployable_cash"]}</div>
        <div class="status-value">€{recommendation['suggested_deployable_cash']:,.0f}</div>
        <div class="status-sub">{T["deployable_cash_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">{T["risk_level"]}</div>
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
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["treasury_insight"]}</div>
    <div class="panel-subtitle">{T["treasury_insight_sub"]}</div>
</div>
""", unsafe_allow_html=True)

if metrics["excess_cash"] > 0:
    st.markdown(f"""
    <div class="insight">
        <b>{liquidity_status} {T["healthy_profile"]}</b><br><br>
        {T["company_holds"]} <b>€{metrics['excess_cash']:,.0f}</b> {T["above_buffer"]}
        {T["yield_text"]} <b>{metrics['annual_yield']*100:.2f}%</b>,
        {T["could_generate"]} <b>€{metrics['annual_potential_return']:,.0f}</b> {T["per_year"]}
        <br><br>
        {T["treasury_score"]}: <b>{treasury_score}/100</b>.
        {T["idle_cash_ratio"]}: <b>{idle_cash_ratio*100:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="warning">
        <b>{T["no_excess"]}</b><br><br>
        {T["no_excess_sub"]}
    </div>
    """, unsafe_allow_html=True)

# AI CFO COPILOT

st.markdown(f"""
<div class="panel">
    <div class="panel-title">AI CFO Copilot</div>
    <div class="panel-subtitle">
        Scenario simulation and treasury decision support.
    </div>
</div>
""", unsafe_allow_html=True)

scenario = st.selectbox(
    "Select CFO scenario",
    [
        "Revenue drops 20%",
        "Hire 2 employees",
        "Increase fixed costs by 15%",
        "Deploy excess liquidity",
        "Protect 6-month runway"
    ],
    key="cfo_scenario_select"
)

scenario_result = ""

if scenario == "Revenue drops 20%":
    simulated_income = metrics["monthly_income"] * 0.80
    simulated_cashflow = simulated_income - metrics["monthly_burn"]

    scenario_result = (
        f"If monthly income drops by 20%, net cashflow would become "
        f"€{simulated_cashflow:,.0f}. "
    )

    if simulated_cashflow < 0:
        scenario_result += (
            "This would create negative monthly cashflow. "
            "Liquidity protection should be prioritized."
        )
    else:
        scenario_result += (
            "The company would still remain cashflow-positive."
        )

elif scenario == "Hire 2 employees":
    estimated_employee_cost = 3500
    added_cost = estimated_employee_cost * 2
    simulated_burn = metrics["monthly_burn"] + added_cost
    simulated_runway = (
        metrics["current_balance"] / simulated_burn
        if simulated_burn > 0
        else 999
    )

    scenario_result = (
        f"Hiring 2 employees would add approximately €{added_cost:,.0f} "
        f"to monthly burn. Estimated runway would become "
        f"{simulated_runway:.1f} months."
    )

elif scenario == "Increase fixed costs by 15%":
    added_cost = metrics["recurring_monthly_total"] * 0.15
    simulated_burn = metrics["monthly_burn"] + added_cost
    simulated_runway = (
        metrics["current_balance"] / simulated_burn
        if simulated_burn > 0
        else 999
    )

    scenario_result = (
        f"A 15% increase in recurring obligations would add approximately "
        f"€{added_cost:,.0f} to monthly burn. Estimated runway would become "
        f"{simulated_runway:.1f} months."
    )

elif scenario == "Deploy excess liquidity":
    deployable = metrics["recommendation"]["suggested_deployable_cash"]

    scenario_result = (
        f"Based on the current protected buffer and recurring obligations, "
        f"approximately €{deployable:,.0f} could potentially be deployed "
        f"while maintaining conservative liquidity coverage."
    )

elif scenario == "Protect 6-month runway":
    required_reserve = metrics["monthly_burn"] * 6
    additional_needed = max(required_reserve - metrics["current_balance"], 0)

    if additional_needed > 0:
        scenario_result = (
            f"To protect a 6-month runway, the company would need approximately "
            f"€{additional_needed:,.0f} additional liquidity."
        )
    else:
        surplus_after_6m = metrics["current_balance"] - required_reserve
        scenario_result = (
            f"The company already covers a 6-month runway. Estimated surplus "
            f"above that reserve is €{surplus_after_6m:,.0f}."
        )

st.markdown(f"""
<div class="insight">
    {scenario_result}
</div>
""", unsafe_allow_html=True)

# AI CFO COPILOT

st.markdown(f"""
<div class="panel">
    <div class="panel-title">AI CFO Copilot</div>
    <div class="panel-subtitle">
        Scenario simulation and treasury decision support.
    </div>
</div>
""", unsafe_allow_html=True)

scenario = st.selectbox(
    "Select CFO scenario",
    [
        "Revenue drops 20%",
        "Hire 2 employees",
        "Increase fixed costs by 15%",
        "Deploy excess liquidity",
        "Protect 6-month runway"
    ]
)

scenario_result = ""

if scenario == "Revenue drops 20%":
    simulated_income = metrics["monthly_income"] * 0.80
    simulated_cashflow = simulated_income - metrics["monthly_burn"]

    scenario_result = (
        f"If monthly income drops by 20%, net cashflow would become "
        f"€{simulated_cashflow:,.0f}. "
    )

    if simulated_cashflow < 0:
        scenario_result += (
            "This would create negative monthly cashflow. "
            "Liquidity protection should be prioritized."
        )
    else:
        scenario_result += (
            "The company would still remain cashflow-positive."
        )

elif scenario == "Hire 2 employees":
    estimated_employee_cost = 3500
    added_cost = estimated_employee_cost * 2
    simulated_burn = metrics["monthly_burn"] + added_cost
    simulated_runway = (
        metrics["current_balance"] / simulated_burn
        if simulated_burn > 0
        else 999
    )

    scenario_result = (
        f"Hiring 2 employees would add approximately €{added_cost:,.0f} "
        f"to monthly burn. Estimated runway would become "
        f"{simulated_runway:.1f} months."
    )

elif scenario == "Increase fixed costs by 15%":
    added_cost = metrics["recurring_monthly_total"] * 0.15
    simulated_burn = metrics["monthly_burn"] + added_cost
    simulated_runway = (
        metrics["current_balance"] / simulated_burn
        if simulated_burn > 0
        else 999
    )

    scenario_result = (
        f"A 15% increase in recurring obligations would add approximately "
        f"€{added_cost:,.0f} to monthly burn. Estimated runway would become "
        f"{simulated_runway:.1f} months."
    )

elif scenario == "Deploy excess liquidity":
    deployable = metrics["recommendation"]["suggested_deployable_cash"]

    scenario_result = (
        f"Based on the current protected buffer and recurring obligations, "
        f"approximately €{deployable:,.0f} could potentially be deployed "
        f"while maintaining conservative liquidity coverage."
    )

elif scenario == "Protect 6-month runway":
    required_reserve = metrics["monthly_burn"] * 6
    additional_needed = max(required_reserve - metrics["current_balance"], 0)

    if additional_needed > 0:
        scenario_result = (
            f"To protect a 6-month runway, the company would need approximately "
            f"€{additional_needed:,.0f} additional liquidity."
        )
    else:
        surplus_after_6m = metrics["current_balance"] - required_reserve
        scenario_result = (
            f"The company already covers a 6-month runway. Estimated surplus "
            f"above that reserve is €{surplus_after_6m:,.0f}."
        )

st.markdown(f"""
<div class="insight">
    {scenario_result}
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["ai_recommendations"]}</div>
    <div class="panel-subtitle">{T["ai_recommendations_sub"]}</div>
</div>
""", unsafe_allow_html=True)

recommendations = []

if metrics["excess_cash"] > 20000:
    if language == "Español":
        recommendations.append(
            f"La liquidez parada sigue siendo elevada. Considera desplegar aproximadamente "
            f"€{metrics['excess_cash']:,.0f} en productos de bajo riesgo y corta duración, "
            f"manteniendo el colchón operativo protegido."
        )
    else:
        recommendations.append(
            f"Idle liquidity remains elevated. Consider deploying approximately "
            f"€{metrics['excess_cash']:,.0f} into short-duration yield products "
            f"while maintaining the protected operating reserve."
        )

if metrics["runway_months"] < 3:
    recommendations.append(
        "El runway de liquidez está por debajo de 3 meses. Se recomienda reducir costes fijos o aumentar reservas."
        if language == "Español"
        else "Liquidity runway is below 3 months. Reducing fixed costs or increasing retained cash reserves is recommended."
    )

if metrics["fixed_cost_ratio"] > 0.60:
    recommendations.append(
        "Las obligaciones recurrentes representan un porcentaje elevado del gasto mensual. Conviene vigilar los compromisos fijos."
        if language == "Español"
        else "Recurring obligations represent a high percentage of monthly burn. Monitoring fixed operational commitments is recommended."
    )

if metrics["recommendation"]["suggested_deployable_cash"] > 10000:
    recommendations.append(
        f"Se estima que €{metrics['recommendation']['suggested_deployable_cash']:,.0f} podrían asignarse a productos treasury de bajo riesgo sin comprometer la liquidez a corto plazo."
        if language == "Español"
        else f"An estimated €{metrics['recommendation']['suggested_deployable_cash']:,.0f} could potentially be allocated into low-risk treasury products without compromising short-term liquidity."
    )

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
        {T["no_ai"]}
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["save_analysis"]}</div>
    <div class="panel-subtitle">{T["save_analysis_sub"]}</div>
</div>
""", unsafe_allow_html=True)

if selected_company_id is not None:
    if st.button(T["save_button"]):
        save_analysis(selected_company_id, metrics)
        st.success(T["saved_ok"])
else:
    st.warning(T["save_warning"])

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["treasury_report"]}</div>
    <div class="panel-subtitle">{T["treasury_report_sub"]}</div>
</div>
""", unsafe_allow_html=True)

if st.button(T["generate_pdf"]):
    pdf_path = generate_treasury_report(metrics)

    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label=T["download_pdf"],
            data=pdf_file,
            file_name="parbat_treasury_report.pdf",
            mime="application/pdf"
        )

if selected_company_id is not None:
    analyses = get_company_analyses(selected_company_id)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["company_history"]}</div>
        <div class="panel-subtitle">{T["company_history_sub"]}</div>
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

        history_df["created_at"] = pd.to_datetime(history_df["created_at"])
        history_df = history_df.sort_values("created_at")

        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info(T["no_history"])

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["transactions"]}</div>
    <div class="panel-subtitle">{T["transactions_sub"]}</div>
</div>
""", unsafe_allow_html=True)

st.dataframe(metrics["df"], use_container_width=True, hide_index=True)