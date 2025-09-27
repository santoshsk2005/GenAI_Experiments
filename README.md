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

The script prints a table with the aggregated totals and displays a chart for a quick visual overview. Use `--chart-type` to choose between `bar`, `stacked`, or `pie` styles.

## Flexible Expense Analytics

`expense_analytics_flexible.py` provides more control over how the data is grouped and filtered.

Example usages:

```bash
# total spend by quarter and category for transactions over $100
python expense_analytics_flexible.py --dimensions quarter category --min-transaction 100

# monthly totals per merchant only showing groups above $500
python expense_analytics_flexible.py --dimensions month merchant --min-total 500
```

Both analytics scripts accept `--chart-type` to control the visualization style.

Available dimensions: `day`, `month`, `quarter`, `year`, `category`, `merchant`.
Use `--min-transaction` and `--max-transaction` to filter transactions by amount and `--min-total` to show only groups exceeding a threshold.

## AI Insurance Rater Webapp

The `webapp` folder contains a Flask application that emulates a third-party auto insurance rater. Instead of calling insurer APIs,
AI-inspired agents parse stored HTML snapshots from Nationwide, GEICO, State Farm, and Allstate to estimate premiums.

### Run locally

```bash
pip install -r requirements.txt
python webapp/app.py
```

Then open [http://localhost:5000](http://localhost:5000) to enter driver and vehicle information and compare projected premiums.
