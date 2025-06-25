import csv
import random
from datetime import datetime, timedelta

# Seed for reproducibility
random.seed(42)

categories = {
    "Groceries": ["Walmart", "Costco", "Trader Joes"],
    "Dining": ["Starbucks", "Chipotle", "McDonalds", "Pizza Hut"],
    "Entertainment": ["Netflix", "Spotify", "AMC Theaters"],
    "Travel": ["Delta Airlines", "Uber", "Airbnb"],
    "Gas": ["Shell", "Chevron", "Exxon"],
    "Online Shopping": ["Amazon", "Ebay", "Etsy"],
    "Utilities": ["Comcast", "PG&E", "Verizon"],
    "Healthcare": ["CVS Pharmacy", "Walgreens", "Health Clinic"],
}

month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

rows = []

for month in range(1, 13):
    num_txn = random.randint(40, 80)
    for _ in range(num_txn):
        day = random.randint(1, month_days[month-1])
        trans_date = datetime(2023, month, day)
        posting_date = trans_date + timedelta(days=random.randint(0, 2))
        category = random.choice(list(categories.keys()))
        merchant = random.choice(categories[category])
        amount = round(random.uniform(5, 500), 2)
        card_last4 = random.randint(1000, 9999)
        txn_id = f"TXN{random.randint(1000000, 9999999)}"
        rows.append([
            trans_date.strftime("%Y-%m-%d"),
            posting_date.strftime("%Y-%m-%d"),
            txn_id,
            merchant,
            category,
            f"{amount:.2f}",
            f"**** **** **** {card_last4}"
        ])

with open("credit_card_statements.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Transaction Date",
        "Posting Date",
        "Transaction ID",
        "Merchant",
        "Category",
        "Amount",
        "Card Number"
    ])
    writer.writerows(sorted(rows))
