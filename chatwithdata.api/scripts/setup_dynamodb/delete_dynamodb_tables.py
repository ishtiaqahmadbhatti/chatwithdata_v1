"""
DynamoDB Table DELETE Script
Deletes all SmartConverter DynamoDB tables permanently.
Asks for confirmation before proceeding.

Usage (activate .venv first):
    python scripts/setup_dynamodb/delete_dynamodb_tables.py   # from project root
    python delete_dynamodb_tables.py                          # from this folder
"""
import os
import sys
import time
import boto3

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
# Read .env — script lives at scripts/setup_dynamodb/ → root is 2 levels up
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

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
PREFIX     = os.environ.get("DYNAMODB_TABLE_PREFIX", "smartconverter")

# ---------------------------------------------------------------------------
# All table names to delete (must match create_dynamodb_tables.py exactly)
# ---------------------------------------------------------------------------
TABLE_NAMES = [
    f"{PREFIX}_atomic_counter",
    f"{PREFIX}_user_list",
    f"{PREFIX}_password_reset_otps",
    f"{PREFIX}_user_subscription_details",
    f"{PREFIX}_request_logs",
    f"{PREFIX}_user_conversion_details",
    f"{PREFIX}_customer_contactus_support_details",
    f"{PREFIX}_customer_feedback_details",
    f"{PREFIX}_customer_frequently_asked_questions_details",
    f"{PREFIX}_customer_general_inquiries_details",
    f"{PREFIX}_customer_technical_support_details",
    f"{PREFIX}_customer_tool_feedback_details",
]


def delete_tables():
    print(danger("\n⚠️  WARNING: This will PERMANENTLY DELETE all SmartConverter DynamoDB tables!"))
    print(f"  Region : {warn(AWS_REGION)}")
    print(f"  Prefix : {warn(PREFIX)}")
    print(f"\n  Tables to delete ({len(TABLE_NAMES)}):")
    for name in TABLE_NAMES:
        print(f"    - {name}")

    print()
    confirm = input(danger("  Type 'DELETE' to confirm, or anything else to cancel: ")).strip()
    if confirm != "DELETE":
        print(warn("\n✖ Cancelled. No tables were deleted."))
        sys.exit(0)

    print()
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    for name in TABLE_NAMES:
        try:
            print(f"  Deleting {name} ...", end=" ")
            table = dynamodb.Table(name)
            table.delete()
            print(ok("✓ deleted"))
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(warn("~ not found (skipped)"))
        except Exception as e:
            print(err(f"✗ ERROR: {e}"))

    print(f"\n{ok('Done. All tables have been deleted.')}")


if __name__ == "__main__":
    delete_tables()
