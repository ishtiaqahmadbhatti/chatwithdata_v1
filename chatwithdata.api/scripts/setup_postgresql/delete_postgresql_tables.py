"""
PostgreSQL Table DELETE Script
Deletes all SmartConverter PostgreSQL tables permanently.
Asks for confirmation before proceeding.

Usage (activate .venv first):
    python scripts/setup_postgresql/delete_postgresql_tables.py   # from project root
    python delete_postgresql_tables.py                            # from this folder
"""
import os
import sys

# ANSI color helpers
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):     return f"{GREEN}{msg}{RESET}"
def warn(msg):   return f"{YELLOW}{msg}{RESET}"
def danger(msg): return f"{RED}{BOLD}{msg}{RESET}"
def err(msg):    return f"{RED}{msg}{RESET}"

# ---------------------------------------------------------------------------
# Read .env — script lives at scripts/setup_postgresql/ → root is 2 levels up
# ---------------------------------------------------------------------------
def _load_env(path: str):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


_script_dir  = os.path.dirname(os.path.abspath(__file__))
_scripts_dir = os.path.dirname(_script_dir)
_root_dir    = os.path.dirname(_scripts_dir)

_load_env(os.path.join(_root_dir, ".env"))

DB_HOST     = os.environ.get("DB_HOST", "localhost")
DB_PORT     = os.environ.get("DB_PORT", "5432")
DB_NAME     = os.environ.get("DB_NAME", "SmartConverterDB")
DB_USER     = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

# ---------------------------------------------------------------------------
# All table names to drop (must match create_postgresql_tables.py exactly)
# ---------------------------------------------------------------------------
TABLE_NAMES = [
    "smartconverter_customer_tool_feedback_details",
    "smartconverter_customer_technical_support_details",
    "smartconverter_customer_feedback_details",
    "smartconverter_customer_frequently_asked_questions_details",
    "smartconverter_customer_general_inquiries_details",
    "smartconverter_customer_contactus_support_details",
    "smartconverter_user_conversion_details",
    "smartconverter_request_logs",
    "smartconverter_user_subscription_details",
    "smartconverter_password_reset_otps",
    "smartconverter_user_list",
]


def delete_tables():
    print(danger("\n⚠️  WARNING: This will PERMANENTLY DELETE all SmartConverter PostgreSQL tables!"))
    print(f"  Host   : {warn(f'{DB_HOST}:{DB_PORT}')}")
    print(f"  DB     : {warn(DB_NAME)}")
    print(f"  User   : {warn(DB_USER)}")
    print(f"\n  Tables to drop ({len(TABLE_NAMES)}):")
    for name in TABLE_NAMES:
        print(f"    - {name}")

    print()
    confirm = input(danger("  Type 'DELETE' to confirm, or anything else to cancel: ")).strip()
    if confirm != "DELETE":
        print(warn("\n✖ Cancelled. No tables were dropped."))
        sys.exit(0)

    print()

    try:
        import psycopg2
    except ImportError:
        print(err("ERROR: psycopg2 is not installed. Run: pip install psycopg2-binary"))
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(err(f"ERROR: Could not connect to PostgreSQL: {e}"))
        sys.exit(1)

    for name in TABLE_NAMES:
        try:
            print(f"  Dropping {name} ...", end=" ")
            cur.execute(f'DROP TABLE IF EXISTS "{name}" CASCADE;')
            print(ok("✓ dropped"))
        except Exception as e:
            print(err(f"✗ ERROR: {e}"))

    cur.close()
    conn.close()
    print(f"\n{ok('Done. All tables have been dropped.')}")


if __name__ == "__main__":
    delete_tables()
