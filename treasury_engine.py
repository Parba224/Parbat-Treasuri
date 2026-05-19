import pandas as pd


def categorize_transaction(description):
    description = str(description).lower()

    categories = {
        "Payroll": ["salary", "payroll"],
        "Rent": ["rent", "office"],
        "Software": ["adobe", "slack", "google", "aws", "hosting", "subscription"],
        "Taxes": ["tax", "vat"],
        "Suppliers": ["supplier", "invoice"],
        "Revenue": ["stripe", "client", "wire", "payment", "payout"],
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in description:
                return category

    return "Other"


def build_expense_summary(df):
    expenses = df[df["amount"] < 0]

    summary = (
        expenses
        .groupby("category")["amount"]
        .sum()
        .abs()
        .reset_index()
    )

    summary.columns = ["category", "total"]

    return summary


def detect_recurring_expenses(df):
    expenses = df[df["amount"] < 0].copy()

    recurring = (
        expenses
        .groupby(["description", "category"])["amount"]
        .agg(["count", "sum", "mean"])
        .reset_index()
    )

    recurring = recurring[recurring["count"] >= 2]

    recurring["monthly_estimate"] = recurring["mean"].abs()
    recurring["total_detected"] = recurring["sum"].abs()

    recurring = recurring[
        [
            "description",
            "category",
            "count",
            "monthly_estimate",
            "total_detected"
        ]
    ]

    recurring = recurring.sort_values(
        by="monthly_estimate",
        ascending=False
    )

    return recurring


def forecast_cash_position(
    current_balance,
    monthly_income,
    recurring_monthly_total,
    forecast_days=30
):
    daily_income = monthly_income / 30
    daily_recurring_costs = recurring_monthly_total / 30

    forecast = []

    projected_balance = current_balance

    for day in range(1, forecast_days + 1):
        projected_balance = (
            projected_balance
            + daily_income
            - daily_recurring_costs
        )

        forecast.append(
            {
                "day": day,
                "projected_balance": projected_balance
            }
        )

    forecast_df = pd.DataFrame(forecast)

    return forecast_df


def generate_risk_alerts(forecast_df, min_cash_buffer):
    below_buffer = forecast_df[
        forecast_df["projected_balance"] < min_cash_buffer
    ]

    if below_buffer.empty:
        return {
            "risk_level": "LOW",
            "message": "Projected liquidity remains above the protected cash buffer.",
            "days_to_buffer_breach": None
        }

    first_breach_day = int(below_buffer["day"].iloc[0])

    return {
        "risk_level": "HIGH",
        "message": f"Projected liquidity may fall below the protected buffer in {first_breach_day} days.",
        "days_to_buffer_breach": first_breach_day
    }


def generate_treasury_recommendation(
    current_balance,
    min_cash_buffer,
    recurring_monthly_total
):
    conservative_reserve = min_cash_buffer + recurring_monthly_total

    suggested_deployable_cash = max(
        current_balance - conservative_reserve,
        0
    )

    return {
        "conservative_reserve": conservative_reserve,
        "suggested_deployable_cash": suggested_deployable_cash
    }


def calculate_treasury_metrics(df, min_cash_buffer, annual_yield):
    df = df.copy()

    df["category"] = df["description"].apply(categorize_transaction)

    current_balance = df["balance"].iloc[-1]
    average_balance = df["balance"].mean()
    min_balance = df["balance"].min()
    max_balance = df["balance"].max()

    excess_cash = max(current_balance - min_cash_buffer, 0)

    annual_potential_return = excess_cash * annual_yield
    monthly_potential_return = annual_potential_return / 12

    income_df = df[df["amount"] > 0]
    expense_df = df[df["amount"] < 0]

    total_income = income_df["amount"].sum()
    total_expenses = abs(expense_df["amount"].sum())

    monthly_income = total_income
    monthly_burn = total_expenses
    net_cashflow = monthly_income - monthly_burn

    runway_months = current_balance / monthly_burn if monthly_burn > 0 else 999

    idle_cash_ratio = excess_cash / current_balance if current_balance > 0 else 0
    cash_efficiency = 1 - idle_cash_ratio

    treasury_score = min(
        100,
        max(0, int(cash_efficiency * 100 + 20))
    )

    expense_summary = build_expense_summary(df)
    recurring_expenses = detect_recurring_expenses(df)

    recurring_monthly_total = (
        recurring_expenses["monthly_estimate"].sum()
        if not recurring_expenses.empty
        else 0
    )

    fixed_cost_ratio = (
        recurring_monthly_total / monthly_burn
        if monthly_burn > 0
        else 0
    )

    forecast_df = forecast_cash_position(
        current_balance=current_balance,
        monthly_income=monthly_income,
        recurring_monthly_total=recurring_monthly_total,
        forecast_days=30
    )

    projected_30_day_balance = (
        forecast_df["projected_balance"].iloc[-1]
        if not forecast_df.empty
        else current_balance
    )

    risk_alert = generate_risk_alerts(
        forecast_df=forecast_df,
        min_cash_buffer=min_cash_buffer
    )

    recommendation = generate_treasury_recommendation(
        current_balance=current_balance,
        min_cash_buffer=min_cash_buffer,
        recurring_monthly_total=recurring_monthly_total
    )

    return {
        "df": df,
        "expense_summary": expense_summary,
        "recurring_expenses": recurring_expenses,
        "forecast_df": forecast_df,
        "risk_alert": risk_alert,
        "recommendation": recommendation,

        "current_balance": current_balance,
        "average_balance": average_balance,
        "min_balance": min_balance,
        "max_balance": max_balance,

        "min_cash_buffer": min_cash_buffer,
        "excess_cash": excess_cash,

        "annual_yield": annual_yield,
        "annual_potential_return": annual_potential_return,
        "monthly_potential_return": monthly_potential_return,

        "monthly_income": monthly_income,
        "monthly_burn": monthly_burn,
        "net_cashflow": net_cashflow,
        "runway_months": runway_months,

        "idle_cash_ratio": idle_cash_ratio,
        "cash_efficiency": cash_efficiency,
        "treasury_score": treasury_score,

        "recurring_monthly_total": recurring_monthly_total,
        "fixed_cost_ratio": fixed_cost_ratio,

        "projected_30_day_balance": projected_30_day_balance,
    }