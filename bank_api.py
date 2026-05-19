import pandas as pd


def clean_number(value):
    if pd.isna(value):
        return 0.0

    value = str(value)
    value = value.replace("€", "")
    value = value.replace("$", "")
    value = value.replace(" ", "")
    value = value.replace(".", "")
    value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return 0.0


def find_column(df, possible_names):
    columns = {
        col.lower().strip(): col
        for col in df.columns
    }

    for name in possible_names:
        name = name.lower().strip()

        if name in columns:
            return columns[name]

    return None


def normalize_bank_data(df):
    df = df.copy()

    date_col = find_column(
        df,
        [
            "date",
            "fecha",
            "booking date",
            "operation date",
            "transaction date",
            "completed date",
            "completed_date"
        ]
    )

    description_col = find_column(
        df,
        [
            "description",
            "concepto",
            "concept",
            "merchant",
            "reference",
            "details",
            "transaction details",
            "name"
        ]
    )

    amount_col = find_column(
        df,
        [
            "amount",
            "importe",
            "value",
            "transaction amount",
            "paid out",
            "paid in",
            "monto"
        ]
    )

    balance_col = find_column(
        df,
        [
            "balance",
            "saldo",
            "running balance",
            "available balance"
        ]
    )

    if date_col is None:
        raise ValueError("No date column found.")

    if description_col is None:
        raise ValueError("No description column found.")

    if amount_col is None:
        raise ValueError("No amount column found.")

    normalized = pd.DataFrame()

    normalized["date"] = pd.to_datetime(
        df[date_col],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    normalized["description"] = df[description_col].astype(str)

    normalized["amount"] = df[amount_col].apply(clean_number)

    if balance_col is not None:
        normalized["balance"] = df[balance_col].apply(clean_number)
    else:
        initial_balance = 0
        normalized["balance"] = normalized["amount"].cumsum() + initial_balance

    normalized = normalized.dropna(subset=["date"])

    normalized = normalized.sort_values("date")

    normalized = normalized.reset_index(drop=True)

    return normalized