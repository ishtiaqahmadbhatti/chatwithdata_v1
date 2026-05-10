# SmartConverter — Database Scripts

All scripts are **self-contained** (read `.env` automatically, no app import needed).  
Always activate your virtual environment first.

```bash
.venv\Scripts\activate
```

---

## 📦 DynamoDB

### ✅ Create Tables
```bash
python scripts/setup_dynamodb/create_dynamodb_tables.py
```

### 🗑️ Delete Tables
```bash
python scripts/setup_dynamodb/delete_dynamodb_tables.py
```

> **Note:** Delete will ask you to type `DELETE` to confirm before proceeding.

---

## 🐘 PostgreSQL

### ✅ Create Tables
```bash
python scripts/setup_postgresql/create_postgresql_tables.py
```

### 🗑️ Delete Tables
```bash
python scripts/setup_postgresql/delete_postgresql_tables.py
```

> **Note:** Delete will ask you to type `DELETE` to confirm before proceeding.

---

## 📁 Folder Structure

```
scripts/
├── README.md                          ← you are here
├── setup_dynamodb/
│   ├── create_dynamodb_tables.py      ← creates 12 DynamoDB tables
│   └── delete_dynamodb_tables.py      ← deletes 12 DynamoDB tables
└── setup_postgresql/
    ├── create_postgresql_tables.py    ← creates 11 PostgreSQL tables
    └── delete_postgresql_tables.py    ← drops 11 PostgreSQL tables
```

---

## 🗃️ Tables Created

### DynamoDB  (`smartconverter_` prefix)
| # | Table |
|---|-------|
| 1 | `smartconverter_atomic_counter` |
| 2 | `smartconverter_user_list` |
| 3 | `smartconverter_password_reset_otps` |
| 4 | `smartconverter_user_subscription_details` |
| 5 | `smartconverter_request_logs` |
| 6 | `smartconverter_user_conversion_details` |
| 7 | `smartconverter_customer_contactus_support_details` |
| 8 | `smartconverter_customer_feedback_details` |
| 9 | `smartconverter_customer_frequently_asked_questions_details` |
| 10 | `smartconverter_customer_general_inquiries_details` |
| 11 | `smartconverter_customer_technical_support_details` |
| 12 | `smartconverter_customer_tool_feedback_details` |

### PostgreSQL  (`smartconverter_` prefix)
| # | Table |
|---|-------|
| 1 | `smartconverter_user_list` |
| 2 | `smartconverter_password_reset_otps` |
| 3 | `smartconverter_user_subscription_details` |
| 4 | `smartconverter_request_logs` |
| 5 | `smartconverter_user_conversion_details` |
| 6 | `smartconverter_customer_contactus_support_details` |
| 7 | `smartconverter_customer_general_inquiries_details` |
| 8 | `smartconverter_customer_frequently_asked_questions_details` |
| 9 | `smartconverter_customer_feedback_details` |
| 10 | `smartconverter_customer_technical_support_details` |
| 11 | `smartconverter_customer_tool_feedback_details` |
