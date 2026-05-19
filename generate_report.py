from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
import os


def money(value):
    return f"€{value:,.0f}"


def build_table(data):
    table = Table(data, colWidths=[230, 230])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
    ]))

    return table


def generate_treasury_report(metrics):
    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/parbat_treasury_report.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=16
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=18,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#334155")
    )

    elements = []

    elements.append(Paragraph("Parbat Treasury Report", title_style))
    elements.append(Paragraph(
        "Automated liquidity intelligence, cash forecasting and treasury optimization report.",
        body_style
    ))
    elements.append(Spacer(1, 18))

    overview_data = [
        ["Metric", "Value"],
        ["Current Cash", money(metrics["current_balance"])],
        ["Protected Buffer", money(metrics["min_cash_buffer"])],
        ["Excess Liquidity", money(metrics["excess_cash"])],
        ["Treasury Score", f"{metrics['treasury_score']}/100"],
        ["Idle Cash Ratio", f"{metrics['idle_cash_ratio'] * 100:.1f}%"],
    ]

    elements.append(Paragraph("Liquidity Overview", section_style))
    elements.append(build_table(overview_data))

    cashflow_data = [
        ["Metric", "Value"],
        ["Monthly Income", money(metrics["monthly_income"])],
        ["Monthly Burn", money(metrics["monthly_burn"])],
        ["Net Cashflow", money(metrics["net_cashflow"])],
        ["Runway Estimate", f"{metrics['runway_months']:.1f} months"],
    ]

    elements.append(Paragraph("Cashflow Analysis", section_style))
    elements.append(build_table(cashflow_data))

    forecast_data = [
        ["Metric", "Value"],
        ["Projected 30-Day Balance", money(metrics["projected_30_day_balance"])],
        ["Risk Level", metrics["risk_alert"]["risk_level"]],
        ["Risk Message", metrics["risk_alert"]["message"]],
        ["Suggested Deployable Cash", money(metrics["recommendation"]["suggested_deployable_cash"])],
        ["Conservative Reserve", money(metrics["recommendation"]["conservative_reserve"])],
    ]

    elements.append(Paragraph("Forecast & Recommendation", section_style))
    elements.append(build_table(forecast_data))

    elements.append(Paragraph("Expense Breakdown", section_style))

    expense_summary = metrics["expense_summary"]

    expense_data = [["Category", "Total"]]

    for _, row in expense_summary.iterrows():
        expense_data.append([
            str(row["category"]),
            money(row["total"])
        ])

    elements.append(build_table(expense_data))

    elements.append(Paragraph("Recurring Expenses", section_style))

    recurring = metrics["recurring_expenses"]

    if recurring.empty:
        elements.append(Paragraph("No recurring expenses detected.", body_style))
    else:
        recurring_data = [["Description", "Category", "Monthly Estimate"]]

        for _, row in recurring.iterrows():
            recurring_data.append([
                str(row["description"]),
                str(row["category"]),
                money(row["monthly_estimate"])
            ])

        elements.append(build_table(recurring_data))

    elements.append(Paragraph("Treasury Insight", section_style))

    insight = f"""
    The company currently holds <b>{money(metrics['excess_cash'])}</b> above its protected operating buffer.
    At an estimated annual yield of <b>{metrics['annual_yield'] * 100:.2f}%</b>, this liquidity could generate
    approximately <b>{money(metrics['annual_potential_return'])}</b> per year.
    <br/><br/>
    Based on current cashflow, recurring obligations and the selected cash buffer, Parbat estimates that
    <b>{money(metrics['recommendation']['suggested_deployable_cash'])}</b> could be considered deployable under
    a conservative liquidity policy.
    """

    elements.append(Paragraph(insight, body_style))

    doc.build(elements)

    return pdf_path