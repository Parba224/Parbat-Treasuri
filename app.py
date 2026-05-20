from supabase import create_client
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import bcrypt

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# =========================
# LOGIN
# =========================

def check_login():

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:

        with st.sidebar:
            st.markdown("### Sesión")
            st.success("Conectado")

            if st.button("Cerrar sesión"):
                st.session_state["authenticated"] = False
                st.rerun()

        return True

    st.title("Tesorería Parbat")
    st.caption("Acceso privado al dashboard treasury.")
    st.markdown("---")

    username = st.text_input("Usuario")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Entrar"):

        if (
            username == st.secrets["auth"]["username"]
            and bcrypt.checkpw(
                password.encode(),
                st.secrets["auth"]["password_hash"].encode()
            )
        ):
            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Usuario o contraseña incorrectos")

    return False


if not check_login():
    st.stop()


# =========================
# TEXTS
# =========================

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
        "platform": "Treasury Intelligence Platform",
        "executive_mode": "Executive Mode",
        "executive_mode_sub": "CFO-level summary of liquidity health, runway and deployable treasury capital.",
        "treasury_score": "Treasury Score",
        "risk_control": "Risk Control",
        "runway_strength": "Runway Strength",
        "deployable_ratio": "Deployable Ratio",
        "current_cash": "Current Cash",
        "protected_buffer": "Protected Buffer",
        "excess_liquidity": "Excess Liquidity",
        "annual_potential": "Annual Potential",
        "monthly_income": "Monthly Income",
        "monthly_burn": "Monthly Burn",
        "net_cashflow": "Net Cashflow",
        "runway": "Runway Estimate",
        "liquidity_overview": "Liquidity Overview",
        "liquidity_overview_sub": "Daily cash balance vs protected buffer.",
        "treasury_products": "Treasury Products Simulator",
        "treasury_products_sub": "Compare low-risk treasury options for excess liquidity.",
        "product": "Product",
        "yield": "Yield",
        "risk": "Risk",
        "liquidity": "Liquidity",
        "allocation": "Allocation",
        "estimated_return": "Estimated Annual Return",
        "cash_forecast": "Cash Forecast",
        "cash_forecast_sub": "30-day projected liquidity based on income and recurring obligations.",
        "save_analysis": "Save Analysis",
        "saved_ok": "Analysis saved successfully.",
        "save_warning": "Create or select a company before saving this analysis.",
        "generate_pdf": "Generate Treasury PDF Report",
        "download_pdf": "Download Treasury Report",
        "history": "Company Analysis History",
        "transactions": "Transactions",
        "available": "Available",
        "minimum_reserve": "Minimum reserve",
        "cash_above_buffer": "Cash above buffer",
        "annual_estimate": "Annual estimate",
        "months": "months",
        "healthy": "HEALTHY",
        "moderate": "MODERATE",
        "critical": "CRITICAL",
        "ai_actions": "AI Treasury Actions",
        "ai_actions_sub": "Automated treasury recommendations based on the current liquidity profile.",
        "alerts": "Treasury Alerts",
        "alerts_sub": "Automated risk, liquidity and opportunity signals.",
        "scenario_simulator": "Scenario Simulator",
        "scenario_simulator_sub": "Compare liquidity resilience under different CFO scenarios.",
    },

    "Español": {
        "upload": "Subir CSV bancario",
        "company": "Empresa",
        "company_name": "Nombre empresa",
        "create_company": "Crear empresa",
        "company_created": "Empresa creada",
        "select_company": "Seleccionar empresa",
        "min_cash_buffer": "Colchón mínimo de caja (€)",
        "annual_yield": "Rentabilidad anual estimada",
        "hero_title": "Parbat Treasury",
        "hero_subtitle": "Inteligencia de liquidez, eficiencia de caja y simulación de rentabilidad para empresas.",
        "platform": "Plataforma de inteligencia treasury",
        "executive_mode": "Modo Ejecutivo",
        "executive_mode_sub": "Resumen ejecutivo CFO del estado de liquidez, runway y capital treasury desplegable.",
        "treasury_score": "Puntuación Treasury",
        "risk_control": "Control de Riesgo",
        "runway_strength": "Fortaleza Runway",
        "deployable_ratio": "Ratio Caja Desplegable",
        "current_cash": "Caja actual",
        "protected_buffer": "Colchón protegido",
        "excess_liquidity": "Liquidez excedente",
        "annual_potential": "Potencial anual",
        "monthly_income": "Ingresos mensuales",
        "monthly_burn": "Gasto mensual",
        "net_cashflow": "Flujo neto de caja",
        "runway": "Runway estimado",
        "liquidity_overview": "Resumen de liquidez",
        "liquidity_overview_sub": "Balance diario de caja frente al colchón protegido.",
        "treasury_products": "Simulador Treasury",
        "treasury_products_sub": "Comparativa de productos treasury de bajo riesgo para la liquidez excedente.",
        "product": "Producto",
        "yield": "Rentabilidad",
        "risk": "Riesgo",
        "liquidity": "Liquidez",
        "allocation": "Asignación",
        "estimated_return": "Rentabilidad anual estimada",
        "cash_forecast": "Previsión de caja",
        "cash_forecast_sub": "Proyección de liquidez a 30 días basada en ingresos y obligaciones recurrentes.",
        "save_analysis": "Guardar análisis",
        "saved_ok": "Análisis guardado correctamente.",
        "save_warning": "Crea o selecciona una empresa antes de guardar este análisis.",
        "generate_pdf": "Generar informe PDF Treasury",
        "download_pdf": "Descargar informe Treasury",
        "history": "Historial de análisis",
        "transactions": "Transacciones",
        "available": "Disponible",
        "minimum_reserve": "Reserva mínima",
        "cash_above_buffer": "Caja sobre colchón",
        "annual_estimate": "Estimación anual",
        "months": "meses",
        "healthy": "SANO",
        "moderate": "MODERADO",
        "critical": "CRÍTICO",
        "ai_actions": "Acciones Treasury IA",
        "ai_actions_sub": "Recomendaciones automáticas según el perfil actual de liquidez.",
        "alerts": "Alertas Treasury",
        "alerts_sub": "Señales automáticas de riesgo, liquidez y oportunidad.",
        "scenario_simulator": "Simulador de Escenarios",
        "scenario_simulator_sub": "Compara la resistencia de liquidez bajo distintos escenarios CFO.",
    }
}


# =========================
# CSS
# =========================

st.markdown("""
<style>
.stApp {
    background: #f4f7fb;
}

.block-container {
    max-width: 1480px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0b1220;
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    color: #0f172a !important;
    background: white !important;
}

[data-testid="stSidebar"] .stButton button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e5e7eb !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}

[data-testid="stSidebar"] .stFileUploader button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e5e7eb !important;
}

[data-testid="stSidebar"] .stFileUploader section {
    background: #ffffff !important;
    border-radius: 10px !important;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 26px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 16px;
}

.platform-label {
    color: #cbd5e1;
    font-size: 14px;
    margin-top: 22px;
}

.panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    padding: 24px;
    margin-top: 24px;
    margin-bottom: 18px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
}

.panel-title {
    font-size: 24px;
    font-weight: 850;
    color: #0f172a;
}

.panel-subtitle {
    color: #64748b;
    margin-top: 6px;
    font-size: 14px;
}

.kpi-card {
    background: #0f172a;
    color: white;
    border-radius: 24px;
    padding: 22px;
    min-height: 140px;
    box-shadow: 0 16px 34px rgba(15, 23, 42, 0.18);
}

.kpi-label {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 12px;
}

.kpi-value {
    font-size: 32px;
    font-weight: 900;
}

.kpi-sub {
    color: #60a5fa;
    font-size: 12px;
    margin-top: 10px;
}

.light-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 20px;
    min-height: 115px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
}

.light-label {
    color: #64748b;
    font-size: 13px;
    margin-bottom: 10px;
}

.light-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 850;
}

.badge-good,
.badge-warn,
.badge-bad {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 13px;
    margin-top: 18px;
}

.badge-good {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
}

.badge-warn {
    background: #fef9c3;
    color: #854d0e;
    border: 1px solid #fde047;
}

.badge-bad {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.score-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.05);
    min-height: 125px;
}

.score-title {
    color: #64748b;
    font-size: 13px;
    margin-bottom: 12px;
    font-weight: 600;
}

.score-value {
    font-size: 32px;
    font-weight: 900;
    color: #0f172a;
    margin-bottom: 16px;
}

.progress-bg {
    width: 100%;
    height: 10px;
    background: #e2e8f0;
    border-radius: 999px;
    overflow: hidden;
}

.insight {
    background: #ecfdf5;
    border-left: 6px solid #22c55e;
    border-radius: 18px;
    padding: 18px;
    color: #064e3b;
    line-height: 1.55;
    margin-bottom: 12px;
}

.warning {
    background: #fff7ed;
    border-left: 6px solid #f97316;
    border-radius: 18px;
    padding: 18px;
    color: #7c2d12;
    line-height: 1.55;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# LANGUAGE
# =========================

language = st.sidebar.selectbox(
    "Language / Idioma",
    ["English", "Español"],
    index=1
)

T = TEXTS[language]


# =========================
# DATA
# =========================

uploaded_file = st.sidebar.file_uploader(
    T["upload"],
    type=["csv"]
)

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
else:
    raw_df = pd.read_csv("data/demo_transactions.csv")

df = normalize_bank_data(raw_df)


# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## Parbat Treasury")
st.sidebar.divider()

st.sidebar.markdown(f"### {T['company']}")

company_name = st.sidebar.text_input(
    T["company_name"],
    value="Demo Company"
)

if st.sidebar.button(T["create_company"]):

    supabase.table("companies").insert({
        "name": company_name
    }).execute()

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


# =========================
# METRICS
# =========================

metrics = calculate_treasury_metrics(
    df,
    min_cash_buffer,
    annual_yield
)

treasury_score = metrics["treasury_score"]

risk_score = 100

if metrics["runway_months"] < 3:
    risk_score -= 35

if metrics["fixed_cost_ratio"] > 0.60:
    risk_score -= 25

if metrics["excess_cash"] <= 0:
    risk_score -= 30

risk_score = max(0, min(100, risk_score))

deployable_cash = metrics["recommendation"]["suggested_deployable_cash"]

deployable_ratio = (
    deployable_cash / metrics["current_balance"] * 100
    if metrics["current_balance"] > 0
    else 0
)

runway_score = min(
    100,
    metrics["runway_months"] / 12 * 100
)

if treasury_score >= 75:
    liquidity_status = T["healthy"]
    badge_class = "badge-good"
elif treasury_score >= 50:
    liquidity_status = T["moderate"]
    badge_class = "badge-warn"
else:
    liquidity_status = T["critical"]
    badge_class = "badge-bad"


# =========================
# HERO
# =========================

st.markdown(f"""
<div class="hero">
    <div class="hero-title">{T["hero_title"]}</div>
    <div class="hero-subtitle">{T["hero_subtitle"]}</div>
    <div class="platform-label">{T["platform"]}</div>
    <span class="{badge_class}">{liquidity_status}</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="panel">
    <div class="panel-title">{T["executive_mode"]}</div>
    <div class="panel-subtitle">{T["executive_mode_sub"]}</div>
</div>
""", unsafe_allow_html=True)


# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Treasury",
    "Forecast",
    "Reports"
])


# =========================
# TAB 1 — OVERVIEW
# =========================

with tab1:

    score1, score2, score3, score4 = st.columns(4)

    score_cards = [
        (T["treasury_score"], treasury_score, "#2563eb"),
        (T["risk_control"], risk_score, "#16a34a"),
        (T["runway_strength"], runway_score, "#9333ea"),
        (T["deployable_ratio"], deployable_ratio, "#f97316"),
    ]

    for col, (title, value, color) in zip(
        [score1, score2, score3, score4],
        score_cards
    ):
        progress = min(max(value, 0), 100)

        with col:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-title">{title}</div>
                <div class="score-value">{value:.0f}</div>
                <div class="progress-bg">
                    <div style="
                        width:{progress}%;
                        height:100%;
                        background:{color};
                        border-radius:999px;
                    "></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    kpis = [
        (T["current_cash"], metrics["current_balance"], T["available"]),
        (T["protected_buffer"], metrics["min_cash_buffer"], T["minimum_reserve"]),
        (T["excess_liquidity"], metrics["excess_cash"], T["cash_above_buffer"]),
        (T["annual_potential"], metrics["annual_potential_return"], T["annual_estimate"]),
    ]

    for col, (label, value, sub) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">€{value:,.0f}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    secondary = [
        (T["monthly_income"], f"€{metrics['monthly_income']:,.0f}"),
        (T["monthly_burn"], f"€{metrics['monthly_burn']:,.0f}"),
        (T["net_cashflow"], f"€{metrics['net_cashflow']:,.0f}"),
        (T["runway"], f"{metrics['runway_months']:.1f} {T['months']}"),
    ]

    for col, (label, value) in zip([s1, s2, s3, s4], secondary):
        with col:
            st.markdown(f"""
            <div class="light-card">
                <div class="light-label">{label}</div>
                <div class="light-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["liquidity_overview"]}</div>
        <div class="panel-subtitle">{T["liquidity_overview_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    fig_balance = go.Figure()

    fig_balance.add_trace(go.Scatter(
        x=df["date"],
        y=df["balance"],
        mode="lines+markers",
        line=dict(width=3, color="#2563eb"),
        marker=dict(size=6, color="#2563eb"),
        name="Balance"
    ))

    fig_balance.add_trace(go.Scatter(
        x=df["date"],
        y=[min_cash_buffer] * len(df),
        mode="lines",
        line=dict(width=2, color="#ef4444", dash="dash"),
        name="Cash buffer"
    ))

    fig_balance.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right")
    )

    st.plotly_chart(fig_balance, use_container_width=True)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["ai_actions"]}</div>
        <div class="panel-subtitle">{T["ai_actions_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    actions = []

    if metrics["excess_cash"] > 10000:
        actions.append({
            "title": "Desplegar liquidez excedente" if language == "Español" else "Deploy excess liquidity",
            "text": (
                f"Desplegar aproximadamente €{deployable_cash:,.0f} en productos treasury de bajo riesgo manteniendo intacto el colchón protegido."
                if language == "Español"
                else f"Deploy approximately €{deployable_cash:,.0f} into low-risk treasury products while keeping the protected buffer intact."
            ),
            "impact": "High"
        })

    if metrics["runway_months"] < 6:
        actions.append({
            "title": "Aumentar protección de runway" if language == "Español" else "Increase runway protection",
            "text": (
                "El runway actual está por debajo del umbral recomendado de 6 meses. Prioriza retener liquidez antes de desplegar capital de forma agresiva."
                if language == "Español"
                else "Current runway is below the recommended 6-month threshold. Prioritize liquidity retention before aggressive deployment."
            ),
            "impact": "High"
        })

    if metrics["fixed_cost_ratio"] > 0.60:
        actions.append({
            "title": "Revisar concentración de costes fijos" if language == "Español" else "Review fixed-cost concentration",
            "text": (
                "Las obligaciones recurrentes representan una parte elevada del gasto mensual. Revisa compromisos fijos antes de aumentar asignación treasury."
                if language == "Español"
                else "Recurring obligations represent a high share of monthly burn. Review fixed commitments before increasing treasury allocation."
            ),
            "impact": "Medium"
        })

    if metrics["net_cashflow"] > 0:
        actions.append({
            "title": "Flujo neto positivo detectado" if language == "Español" else "Positive net cashflow detected",
            "text": (
                "La empresa genera flujo de caja mensual positivo. Esto permite una estrategia controlada de despliegue treasury."
                if language == "Español"
                else "The company is generating positive monthly cashflow. This supports a controlled treasury deployment plan."
            ),
            "impact": "Medium"
        })

    if not actions:
        actions.append({
            "title": "Mantener seguimiento" if language == "Español" else "Maintain monitoring",
            "text": (
                "Perfil de liquidez estable. Continúa con seguimiento mensual antes de cambiar la asignación treasury."
                if language == "Español"
                else "Liquidity profile is stable. Continue monthly monitoring before changing treasury allocation."
            ),
            "impact": "Low"
        })

    for action in actions:
        impact_label = (
            "Alto impacto" if language == "Español" and action["impact"] == "High"
            else "Impacto medio" if language == "Español" and action["impact"] == "Medium"
            else "Bajo impacto" if language == "Español"
            else f"{action['impact']} impact"
        )

        with st.container(border=True):
            left, right = st.columns([5, 1])

            with left:
                st.markdown(f"### {action['title']}")
                st.caption(action["text"])

            with right:
                st.markdown("<br>", unsafe_allow_html=True)

                if action["impact"] == "High":
                    st.success(impact_label)
                elif action["impact"] == "Medium":
                    st.warning(impact_label)
                else:
                    st.info(impact_label)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["alerts"]}</div>
        <div class="panel-subtitle">{T["alerts_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    alerts = []

    if metrics["runway_months"] < 3:
        alerts.append({
            "level": "critical",
            "title": "Runway crítico" if language == "Español" else "Critical runway",
            "message": (
                "El runway está por debajo de 3 meses. Prioriza caja y reduce despliegue treasury."
                if language == "Español"
                else "Runway is below 3 months. Prioritize cash protection and reduce treasury deployment."
            )
        })

    if metrics["excess_cash"] > 25000:
        alerts.append({
            "level": "opportunity",
            "title": "Oportunidad de rentabilidad" if language == "Español" else "Yield opportunity",
            "message": (
                f"Hay €{metrics['excess_cash']:,.0f} por encima del colchón protegido. Existe oportunidad de asignación treasury."
                if language == "Español"
                else f"There is €{metrics['excess_cash']:,.0f} above the protected buffer. Treasury allocation opportunity detected."
            )
        })

    if metrics["fixed_cost_ratio"] > 0.60:
        alerts.append({
            "level": "warning",
            "title": "Costes fijos elevados" if language == "Español" else "High fixed costs",
            "message": (
                "Los costes recurrentes pesan demasiado sobre el gasto mensual. Revisa compromisos fijos."
                if language == "Español"
                else "Recurring costs represent a high share of monthly burn. Review fixed commitments."
            )
        })

    if metrics["net_cashflow"] > 0 and metrics["excess_cash"] > 0:
        alerts.append({
            "level": "positive",
            "title": "Perfil financiero positivo" if language == "Español" else "Positive financial profile",
            "message": (
                "La empresa tiene flujo neto positivo y liquidez excedente. Perfil apto para treasury controlado."
                if language == "Español"
                else "Company has positive net cashflow and excess liquidity. Suitable for controlled treasury allocation."
            )
        })

    if not alerts:
        alerts.append({
            "level": "neutral",
            "title": "Sin alertas relevantes" if language == "Español" else "No relevant alerts",
            "message": (
                "No se detectan señales relevantes de riesgo u oportunidad."
                if language == "Español"
                else "No relevant risk or opportunity signals detected."
            )
        })

    for alert in alerts:
        if alert["level"] == "critical":
            st.error(f"🚨 {alert['title']} — {alert['message']}")
        elif alert["level"] == "warning":
            st.warning(f"⚠️ {alert['title']} — {alert['message']}")
        elif alert["level"] == "opportunity":
            st.info(f"💡 {alert['title']} — {alert['message']}")
        elif alert["level"] == "positive":
            st.success(f"✅ {alert['title']} — {alert['message']}")
        else:
            st.info(f"ℹ️ {alert['title']} — {alert['message']}")


# =========================
# TAB 2 — TREASURY
# =========================

with tab2:

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["treasury_products"]}</div>
        <div class="panel-subtitle">{T["treasury_products_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    products = pd.DataFrame([
        {
            T["product"]: "Cuenta remunerada",
            T["yield"]: 0.023,
            T["risk"]: "Bajo",
            T["liquidity"]: "Instantánea",
            T["allocation"]: deployable_cash * 0.35,
        },
        {
            T["product"]: "Fondo monetario",
            T["yield"]: 0.031,
            T["risk"]: "Bajo",
            T["liquidity"]: "24h",
            T["allocation"]: deployable_cash * 0.40,
        },
        {
            T["product"]: "T-Bills",
            T["yield"]: 0.037,
            T["risk"]: "Muy bajo",
            T["liquidity"]: "1-2 días",
            T["allocation"]: deployable_cash * 0.25,
        },
    ])

    products[T["estimated_return"]] = (
        products[T["allocation"]] *
        products[T["yield"]]
    )

    total_return = products[T["estimated_return"]].sum()

    p1, p2 = st.columns([1.4, 1])

    with p1:
        display_products = products.copy()

        display_products[T["yield"]] = display_products[T["yield"]].apply(
            lambda x: f"{x*100:.2f}%"
        )

        display_products[T["allocation"]] = display_products[T["allocation"]].apply(
            lambda x: f"€{x:,.0f}"
        )

        display_products[T["estimated_return"]] = display_products[T["estimated_return"]].apply(
            lambda x: f"€{x:,.0f}"
        )

        st.dataframe(
            display_products,
            use_container_width=True,
            hide_index=True
        )

    with p2:
        fig_products = px.pie(
            products,
            names=T["product"],
            values=T["allocation"],
            hole=0.55
        )

        fig_products.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white",
            font=dict(color="#0f172a")
        )

        st.plotly_chart(
            fig_products,
            use_container_width=True
        )

    st.markdown(f"""
    <div class="insight">
        <b>{T["estimated_return"]}:</b> €{total_return:,.0f}
    </div>
    """, unsafe_allow_html=True)


# =========================
# TAB 3 — FORECAST
# =========================

with tab3:

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["cash_forecast"]}</div>
        <div class="panel-subtitle">{T["cash_forecast_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    forecast_df = metrics["forecast_df"]

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
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right")
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["scenario_simulator"]}</div>
        <div class="panel-subtitle">{T["scenario_simulator_sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

    base_runway = metrics["runway_months"]

    scenario_data = pd.DataFrame([
        {
            "Scenario": "Base Case",
            "Monthly Income": metrics["monthly_income"],
            "Monthly Burn": metrics["monthly_burn"],
            "Net Cashflow": metrics["net_cashflow"],
            "Runway": base_runway,
        },
        {
            "Scenario": "Stress Case",
            "Monthly Income": metrics["monthly_income"] * 0.80,
            "Monthly Burn": metrics["monthly_burn"] * 1.10,
            "Net Cashflow": (metrics["monthly_income"] * 0.80) - (metrics["monthly_burn"] * 1.10),
            "Runway": metrics["current_balance"] / (metrics["monthly_burn"] * 1.10) if metrics["monthly_burn"] > 0 else 999,
        },
        {
            "Scenario": "Growth Case",
            "Monthly Income": metrics["monthly_income"] * 1.15,
            "Monthly Burn": metrics["monthly_burn"] * 1.20,
            "Net Cashflow": (metrics["monthly_income"] * 1.15) - (metrics["monthly_burn"] * 1.20),
            "Runway": metrics["current_balance"] / (metrics["monthly_burn"] * 1.20) if metrics["monthly_burn"] > 0 else 999,
        },
    ])

    c1, c2, c3 = st.columns(3)

    for col, row in zip([c1, c2, c3], scenario_data.to_dict("records")):
        scenario_name = row["Scenario"]

        if language == "Español":
            scenario_name = scenario_name.replace("Base Case", "Escenario Base")
            scenario_name = scenario_name.replace("Stress Case", "Escenario Estrés")
            scenario_name = scenario_name.replace("Growth Case", "Escenario Crecimiento")

        with col:
            with st.container(border=True):

                st.markdown(f"### {scenario_name}")

                st.caption(
                    "Flujo neto"
                    if language == "Español"
                    else "Net Cashflow"
                )

                st.metric(
                    label="",
                    value=f"€{row['Net Cashflow']:,.0f}"
                )

                st.caption("Runway")

                st.metric(
                    label="",
                    value=f"{row['Runway']:.1f} {T['months']}"
                )

    scenario_display = scenario_data.copy()

    if language == "Español":
        scenario_display["Scenario"] = scenario_display["Scenario"].replace({
            "Base Case": "Escenario Base",
            "Stress Case": "Escenario Estrés",
            "Growth Case": "Escenario Crecimiento",
        })

    scenario_display["Monthly Income"] = scenario_display["Monthly Income"].apply(lambda x: f"€{x:,.0f}")
    scenario_display["Monthly Burn"] = scenario_display["Monthly Burn"].apply(lambda x: f"€{x:,.0f}")
    scenario_display["Net Cashflow"] = scenario_display["Net Cashflow"].apply(lambda x: f"€{x:,.0f}")
    scenario_display["Runway"] = scenario_display["Runway"].apply(lambda x: f"{x:.1f} {T['months']}")

    if language == "Español":
        scenario_display = scenario_display.rename(columns={
            "Scenario": "Escenario",
            "Monthly Income": "Ingresos mensuales",
            "Monthly Burn": "Gasto mensual",
            "Net Cashflow": "Flujo neto",
            "Runway": "Runway",
        })

    st.dataframe(
        scenario_display,
        use_container_width=True,
        hide_index=True
    )


# =========================
# TAB 4 — REPORTS
# =========================

with tab4:

    st.markdown(f"""
    <div class="panel">
       <div class="panel-title">
           {"Vista Global Empresas" if language == "Español" else "Multi-Company Overview"}
       </div>

       <div class="panel-subtitle">
           {
               "Resumen CFO consolidado de todas las compañías registradas."
               if language == "Español"
               else "Consolidated CFO summary across all registered companies."
           }
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_companies = get_companies()

    multi_rows = []

    for company_id, company_name in all_companies:

        simulated_cash = metrics["current_balance"] * (
            0.7 + (company_id * 0.12)
        )

        simulated_runway = metrics["runway_months"] * (
            0.8 + (company_id * 0.08)
        )

        simulated_score = min(
            100,
            treasury_score * (
                0.85 + (company_id * 0.05)
            )
        )

        if simulated_score >= 75:
            status = (
                "SANO"
                if language == "Español"
                else "HEALTHY"
            )

        elif simulated_score >= 50:
            status = (
                "MODERADO"
                if language == "Español"
                else "MODERATE"
            )

        else:
            status = (
                "CRÍTICO"
                if language == "Español"
                else "CRITICAL"
            )

        multi_rows.append({
            "Empresa" if language == "Español" else "Company": company_name,
            "Caja" if language == "Español" else "Cash": f"€{simulated_cash:,.0f}",
            "Runway": f"{simulated_runway:.1f} {T['months']}",
            "Treasury Score": f"{simulated_score:.0f}",
            "Estado" if language == "Español" else "Status": status
        })

    multi_df = pd.DataFrame(multi_rows)

    st.dataframe(
        multi_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["save_analysis"]}</div>
    </div>
    """, unsafe_allow_html=True)

    if selected_company_id is not None:
        if st.button(T["save_analysis"]):
            save_analysis(selected_company_id, metrics)
            st.success(T["saved_ok"])
    else:
        st.warning(T["save_warning"])

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["generate_pdf"]}</div>
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
            <div class="panel-title">{T["history"]}</div>
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

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No saved analyses yet.")

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{T["transactions"]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        metrics["df"],
        use_container_width=True,
        hide_index=True
    )