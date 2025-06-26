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

## Flexible Expense Analytics

`expense_analytics_flexible.py` provides more control over how the data is grouped and filtered.

Example usages:

```bash
# total spend by quarter and category for transactions over $100
python expense_analytics_flexible.py --dimensions quarter category --min-transaction 100

# monthly totals per merchant only showing groups above $500
python expense_analytics_flexible.py --dimensions month merchant --min-total 500
```

Available dimensions: `day`, `month`, `quarter`, `year`, `category`, `merchant`.
Use `--min-transaction` and `--max-transaction` to filter transactions by amount and `--min-total` to show only groups exceeding a threshold.
