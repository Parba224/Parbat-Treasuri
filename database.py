import sqlite3
from datetime import datetime


DB_PATH = "data/parbat_treasury.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        current_cash REAL,
        protected_buffer REAL,
        excess_liquidity REAL,
        treasury_score REAL,
        monthly_income REAL,
        monthly_burn REAL,
        net_cashflow REAL,
        runway_months REAL,
        projected_30_day_balance REAL,
        suggested_deployable_cash REAL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)

    conn.commit()
    conn.close()


def create_company(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO companies (name, created_at)
        VALUES (?, ?)
        """,
        (name, datetime.now().isoformat())
    )

    conn.commit()
    company_id = cursor.lastrowid
    conn.close()

    return company_id


def get_companies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name
    FROM companies
    ORDER BY created_at DESC
    """)

    companies = cursor.fetchall()
    conn.close()

    return companies


def save_analysis(company_id, metrics):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analyses (
            company_id,
            current_cash,
            protected_buffer,
            excess_liquidity,
            treasury_score,
            monthly_income,
            monthly_burn,
            net_cashflow,
            runway_months,
            projected_30_day_balance,
            suggested_deployable_cash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            metrics["current_balance"],
            metrics["min_cash_buffer"],
            metrics["excess_cash"],
            metrics["treasury_score"],
            metrics["monthly_income"],
            metrics["monthly_burn"],
            metrics["net_cashflow"],
            metrics["runway_months"],
            metrics["projected_30_day_balance"],
            metrics["recommendation"]["suggested_deployable_cash"],
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_company_analyses(company_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            created_at,
            current_cash,
            excess_liquidity,
            treasury_score,
            projected_30_day_balance,
            suggested_deployable_cash
        FROM analyses
        WHERE company_id = ?
        ORDER BY created_at DESC
        """,
        (company_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows