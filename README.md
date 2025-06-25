# GenAI_Experiments

Synthetic data generation scripts.

## Household Expenses

The `generate_expenses.py` script creates a sample `expenses.csv` file with random monthly expenses for 2023.

Run:

```bash
python generate_expenses.py
```

## Credit Card Statement

The `generate_credit_card_statements.py` script builds a more detailed `credit_card_statements.csv` dataset that mimics a credit card statement. Each entry includes transaction and posting dates, a transaction ID, merchant name, category, amount, and a masked card number.

Run:

```bash
python generate_credit_card_statements.py
```

## Expense Analytics

Use `expense_analytics.py` to explore spending patterns in `credit_card_statements.csv`.

You can group totals by month, category, or both:

```bash
# group by month
python expense_analytics.py --dimensions month

# group by category
python expense_analytics.py --dimensions category

# group by both month and category
python expense_analytics.py --dimensions month category
```

The script prints a table with the aggregated totals and displays a simple bar chart for a quick visual overview.
