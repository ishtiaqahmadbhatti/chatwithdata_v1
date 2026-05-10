"""
DynamoDB Table Setup Script
Creates all DynamoDB tables for SmartConverter.
Tables are NOT auto-created when the API starts — run this ONCE manually.

Usage (activate .venv first):
    python scripts/setup_dynamodb/create_dynamodb_tables.py   # from project root
    python create_dynamodb_tables.py                          # from this folder
"""
import os
import sys
import boto3

# ANSI color helpers
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"

def ok(msg):   return f"{GREEN}{msg}{RESET}"
def warn(msg): return f"{YELLOW}{msg}{RESET}"
def err(msg):  return f"{RED}{msg}{RESET}"

# ---------------------------------------------------------------------------
# Read .env manually — self-contained, no 'app' import needed.
# Script lives at:  scripts/setup_dynamodb/create_dynamodb_tables.py
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


_script_dir = os.path.dirname(os.path.abspath(__file__))          # .../scripts/setup_dynamodb/
_scripts_dir = os.path.dirname(_script_dir)                        # .../scripts/
_root_dir   = os.path.dirname(_scripts_dir)                        # project root

_load_env(os.path.join(_root_dir, ".env"))

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
PREFIX     = os.environ.get("DYNAMODB_TABLE_PREFIX", "smartconverter")

# ---------------------------------------------------------------------------
# Table definitions
# Final name = PREFIX + "_" + suffix  →  e.g. smartconverter_user_list
# ---------------------------------------------------------------------------
TABLES = [
    # ---- Internal / Utility ----
    {
        "TableName": f"{PREFIX}_atomic_counter",
        "KeySchema": [{"AttributeName": "table_name", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "table_name", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },

    # ---- Core User Tables ----
    {
        "TableName": f"{PREFIX}_user_list",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id",        "AttributeType": "N"},
            {"AttributeName": "email",     "AttributeType": "S"},
            {"AttributeName": "device_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "EmailIndex",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "DeviceIdIndex",
                "KeySchema": [{"AttributeName": "device_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_password_reset_otps",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id",    "AttributeType": "N"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "EmailIndex",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_user_subscription_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id",      "AttributeType": "N"},
            {"AttributeName": "user_id", "AttributeType": "N"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "UserIdIndex",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },

    # ---- Logging / Activity ----
    {
        "TableName": f"{PREFIX}_request_logs",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_user_conversion_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id",      "AttributeType": "N"},
            {"AttributeName": "user_id", "AttributeType": "N"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "UserIdIndex",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },

    # ---- Helpdesk Tables ----
    {
        "TableName": f"{PREFIX}_customer_contactus_support_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_customer_feedback_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_customer_frequently_asked_questions_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_customer_general_inquiries_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_customer_technical_support_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": f"{PREFIX}_customer_tool_feedback_details",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
]


def create_tables():
    print(f"Connecting to DynamoDB  →  region: {ok(AWS_REGION)}")
    print(f"Table prefix            →  {ok(PREFIX)}\n")
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    for table_info in TABLES:
        name = table_info["TableName"]
        try:
            print(f"  Creating {name} ...", end=" ")
            dynamodb.create_table(**table_info)
            print(ok("✓ initiated"))
        except dynamodb.meta.client.exceptions.ResourceInUseException:
            print(warn("~ already exists"))
        except Exception as e:
            print(err(f"✗ ERROR: {e}"))

    print(f"\n{ok('All DynamoDB tables are ready.')}")


if __name__ == "__main__":
    create_tables()
