"""
PostgreSQL Table Setup Script
Creates all PostgreSQL tables for SmartConverter.
Tables are NOT auto-created when the API starts — run this ONCE manually.

Usage (activate .venv first):
    python scripts/setup_postgresql/create_postgresql_tables.py   # from project root
    python create_postgresql_tables.py                            # from this folder
"""
import os
import sys

# ANSI color helpers
GREEN  = "\033[92m"
RED    = "\033[91m"
RESET  = "\033[0m"

def ok(msg):  return f"{GREEN}{msg}{RESET}"
def err(msg): return f"{RED}{msg}{RESET}"

# ---------------------------------------------------------------------------
# Read .env manually — self-contained, no 'app' import needed.
# Script lives at:  scripts/setup_postgresql/create_postgresql_tables.py
# Project root is:  two levels up.
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


_script_dir  = os.path.dirname(os.path.abspath(__file__))          # .../scripts/setup_postgresql/
_scripts_dir = os.path.dirname(_script_dir)                         # .../scripts/
_root_dir    = os.path.dirname(_scripts_dir)                        # project root

_load_env(os.path.join(_root_dir, ".env"))

# ---------------------------------------------------------------------------
# Read connection settings
# ---------------------------------------------------------------------------
DB_HOST     = os.environ.get("DB_HOST", "localhost")
DB_PORT     = os.environ.get("DB_PORT", "5432")
DB_NAME     = os.environ.get("DB_NAME", "SmartConverterDB")
DB_USER     = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

# ---------------------------------------------------------------------------
# Table definitions (must match the SQLAlchemy models exactly)
# All tables use the smartconverter_ prefix.
# ---------------------------------------------------------------------------
CREATE_STATEMENTS = [

    # ---- Core User Tables ----
    """
    CREATE TABLE IF NOT EXISTS smartconverter_user_list (
        id                SERIAL PRIMARY KEY,
        created_at        TIMESTAMPTZ DEFAULT NOW(),
        modified_at       TIMESTAMPTZ,
        first_name        VARCHAR(100),
        last_name         VARCHAR(100),
        gender            VARCHAR(50),
        phone_number      VARCHAR(20),
        email             VARCHAR(255) UNIQUE,
        profile_image_url VARCHAR(500),
        password          VARCHAR(255),
        device_id         VARCHAR(255)
    );
    CREATE INDEX IF NOT EXISTS ix_smartconverter_user_list_email     ON smartconverter_user_list (email);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_user_list_device_id ON smartconverter_user_list (device_id);
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_password_reset_otps (
        id          SERIAL PRIMARY KEY,
        email       VARCHAR NOT NULL,
        otp_code    VARCHAR NOT NULL,
        full_name   VARCHAR,
        device_id   VARCHAR,
        expires_at  TIMESTAMP NOT NULL,
        is_used     BOOLEAN DEFAULT FALSE,
        created_at  TIMESTAMP DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS ix_smartconverter_password_reset_otps_email ON smartconverter_password_reset_otps (email);
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_user_subscription_details (
        id                     SERIAL PRIMARY KEY,
        created_at             TIMESTAMPTZ DEFAULT NOW(),
        modified_at            TIMESTAMPTZ,
        user_id                INTEGER NOT NULL UNIQUE,
        is_premium             BOOLEAN DEFAULT FALSE,
        subscription_plan      VARCHAR(50) DEFAULT 'free',
        subscription_expiry    TIMESTAMPTZ,
        stripe_customer_id     VARCHAR(100),
        stripe_subscription_id VARCHAR(100),
        subscription_status    VARCHAR(50) DEFAULT 'inactive'
    );
    CREATE INDEX IF NOT EXISTS ix_smartconverter_user_subscription_details_stripe_customer_id
        ON smartconverter_user_subscription_details (stripe_customer_id);
    """,

    # ---- Logging / Activity ----
    """
    CREATE TABLE IF NOT EXISTS smartconverter_request_logs (
        id              SERIAL PRIMARY KEY,
        client_id       VARCHAR(64),
        session_id      VARCHAR(64),
        request_id      VARCHAR(64),
        method          VARCHAR(10) NOT NULL,
        path            VARCHAR(512) NOT NULL,
        query_string    TEXT,
        status_code     INTEGER,
        latency_ms      INTEGER,
        source          VARCHAR(32),
        ip              VARCHAR(64),
        x_forwarded_for VARCHAR(256),
        user_agent      TEXT,
        origin          VARCHAR(256),
        referer         VARCHAR(512),
        device_type     VARCHAR(32),
        os              VARCHAR(64),
        browser         VARCHAR(64),
        app_platform    VARCHAR(64),
        app_version     VARCHAR(64),
        device_id       VARCHAR(128),
        is_docs         BOOLEAN DEFAULT FALSE,
        is_download     BOOLEAN DEFAULT FALSE,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_client_id  ON smartconverter_request_logs (client_id);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_session_id ON smartconverter_request_logs (session_id);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_request_id ON smartconverter_request_logs (request_id);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_path       ON smartconverter_request_logs (path);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_source     ON smartconverter_request_logs (source);
    CREATE INDEX IF NOT EXISTS ix_smartconverter_request_logs_ip         ON smartconverter_request_logs (ip);
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_user_conversion_details (
        id               SERIAL PRIMARY KEY,
        created_at       TIMESTAMPTZ DEFAULT NOW(),
        modified_at      TIMESTAMPTZ,
        user_id          INTEGER,
        conversion_type  VARCHAR(100) NOT NULL,
        input_filename   VARCHAR(500) NOT NULL,
        input_file_size  BIGINT,
        input_file_type  VARCHAR(50),
        output_filename  VARCHAR(500),
        output_file_size BIGINT,
        output_file_type VARCHAR(50),
        status           VARCHAR(50) DEFAULT 'pending',
        error_message    TEXT,
        ip_address       VARCHAR(50),
        user_agent       VARCHAR(500),
        method           VARCHAR(10),
        api_endpoint     VARCHAR(200)
    );
    CREATE INDEX IF NOT EXISTS ix_smartconverter_user_conversion_details_user_id ON smartconverter_user_conversion_details (user_id);
    """,

    # ---- Helpdesk Tables ----
    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_contactus_support_details (
        id         SERIAL PRIMARY KEY,
        full_name  VARCHAR NOT NULL,
        email      VARCHAR NOT NULL,
        subject    VARCHAR NOT NULL,
        message    TEXT NOT NULL,
        user_id    INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_general_inquiries_details (
        id              SERIAL PRIMARY KEY,
        full_name       VARCHAR NOT NULL,
        email           VARCHAR NOT NULL,
        subject         VARCHAR NOT NULL,
        query           TEXT NOT NULL,
        attachment_path VARCHAR,
        user_id         INTEGER,
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_frequently_asked_questions_details (
        id         SERIAL PRIMARY KEY,
        question   VARCHAR NOT NULL,
        category   VARCHAR,
        user_email VARCHAR,
        user_id    INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_feedback_details (
        id         SERIAL PRIMARY KEY,
        full_name  VARCHAR,
        email      VARCHAR,
        feedback   TEXT NOT NULL,
        rating     INTEGER,
        user_id    INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_technical_support_details (
        id              SERIAL PRIMARY KEY,
        full_name       VARCHAR NOT NULL,
        email           VARCHAR NOT NULL,
        issue_type      VARCHAR NOT NULL,
        description     TEXT NOT NULL,
        os_info         VARCHAR,
        browser_info    VARCHAR,
        attachment_path VARCHAR,
        user_id         INTEGER,
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS smartconverter_customer_tool_feedback_details (
        id         SERIAL PRIMARY KEY,
        tool_name  VARCHAR NOT NULL,
        category   VARCHAR,
        rating     INTEGER NOT NULL,
        feedback   TEXT,
        user_email VARCHAR,
        user_id    INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
]

# Human-readable names for progress output (same order as CREATE_STATEMENTS)
TABLE_NAMES = [
    "smartconverter_user_list",
    "smartconverter_password_reset_otps",
    "smartconverter_user_subscription_details",
    "smartconverter_request_logs",
    "smartconverter_user_conversion_details",
    "smartconverter_customer_contactus_support_details",
    "smartconverter_customer_general_inquiries_details",
    "smartconverter_customer_frequently_asked_questions_details",
    "smartconverter_customer_feedback_details",
    "smartconverter_customer_technical_support_details",
    "smartconverter_customer_tool_feedback_details",
]


def create_tables():
    try:
        import psycopg2
    except ImportError:
        print(err("ERROR: psycopg2 is not installed. Run: pip install psycopg2-binary"))
        sys.exit(1)

    print(f"Connecting to PostgreSQL  →  {ok(f'{DB_HOST}:{DB_PORT}/{DB_NAME}')}  as  {ok(DB_USER)}\n")

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

    for name, sql in zip(TABLE_NAMES, CREATE_STATEMENTS):
        try:
            print(f"  Creating {name} ...", end=" ")
            cur.execute(sql)
            print(ok("✓ done"))
        except Exception as e:
            print(err(f"✗ ERROR: {e}"))

    cur.close()
    conn.close()
    print(f"\n{ok('All PostgreSQL tables are ready.')}")


if __name__ == "__main__":
    create_tables()
