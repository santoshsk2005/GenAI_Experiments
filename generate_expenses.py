import csv
import random
from datetime import datetime, timedelta

categories = [
    "Rent", "Utilities", "Groceries", "Dining", "Transportation",
    "Internet", "Insurance", "Healthcare", "Entertainment",
    "Vacation", "Office Travel", "Miscellaneous"
]

month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

random.seed(42)

rows = []

for month in range(1, 13):
    for t in range(75):
        day = random.randint(1, month_days[month-1])
        date = datetime(2023, month, day)
        category = random.choice(categories)
        if category == "Rent":
            amount = 1500
            description = "Monthly Rent"
        elif category == "Utilities":
            amount = random.uniform(80, 200)
            description = "Utility Bill"
        elif category == "Groceries":
            amount = random.uniform(20, 150)
            description = "Groceries"
        elif category == "Dining":
            amount = random.uniform(15, 70)
            description = "Dining Out"
        elif category == "Transportation":
            amount = random.uniform(10, 60)
            description = "Public Transport or Fuel"
        elif category == "Internet":
            amount = 60
            description = "Internet Bill"
        elif category == "Insurance":
            amount = random.uniform(100, 300)
            description = "Insurance Payment"
        elif category == "Healthcare":
            amount = random.uniform(50, 250)
            description = "Medical Expense"
        elif category == "Entertainment":
            amount = random.uniform(15, 120)
            description = "Entertainment"
        elif category == "Vacation":
            amount = random.uniform(200, 1500)
            description = "Vacation Expense"
        elif category == "Office Travel":
            amount = random.uniform(50, 600)
            description = "Office Travel"
        else:
            amount = random.uniform(10, 100)
            description = "Misc Expense"

        rows.append([
            date.strftime("%Y-%m-%d"),
            category,
            description,
            f"{amount:.2f}"
        ])

with open("expenses.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "Category", "Description", "Amount"])
    writer.writerows(sorted(rows))
