import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_data(csv_path: str) -> pd.DataFrame:
    """Load the credit card statement CSV and add time dimensions."""
    df = pd.read_csv(
        csv_path,
        parse_dates=["Transaction Date", "Posting Date"],
    )
    df["Amount"] = df["Amount"].astype(float)
    df["Day"] = df["Transaction Date"].dt.date.astype(str)
    df["Month"] = df["Transaction Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Transaction Date"].dt.to_period("Q").astype(str)
    df["Year"] = df["Transaction Date"].dt.year.astype(str)
    return df


def filter_transactions(
    df: pd.DataFrame,
    min_amount: float | None = None,
    max_amount: float | None = None,
) -> pd.DataFrame:
    """Filter transactions by amount thresholds."""
    if min_amount is not None:
        df = df[df["Amount"] >= min_amount]
    if max_amount is not None:
        df = df[df["Amount"] <= max_amount]
    return df


def aggregate_spending(
    df: pd.DataFrame,
    dimensions: list[str],
    min_total: float | None = None,
) -> pd.DataFrame:
    """Aggregate spending along the requested dimensions."""
    available_dims = {
        "day": "Day",
        "month": "Month",
        "quarter": "Quarter",
        "year": "Year",
        "category": "Category",
        "merchant": "Merchant",
    }
    cols = [available_dims[d] for d in dimensions]
    summary = df.groupby(cols)["Amount"].sum().reset_index()
    if min_total is not None:
        summary = summary[summary["Amount"] >= min_total]
    return summary


def display(summary: pd.DataFrame, dimensions: list[str], chart_type: str) -> None:
    """Pretty-print the summary and plot a chart."""
    print("\nSpending Summary:\n")
    print(summary.to_string(index=False))

    if len(dimensions) == 1:
        if chart_type == "pie":
            summary.set_index(dimensions[0])["Amount"].plot.pie(autopct="%.1f%%")
        else:  # bar
            summary.plot.bar(x=dimensions[0], y="Amount", legend=False)
        plt.ylabel("Total Spend ($)")
        plt.tight_layout()
        plt.show()
    elif len(dimensions) == 2:
        pivot = summary.pivot(index=dimensions[0], columns=dimensions[1], values="Amount")
        if chart_type == "stacked":
            pivot.plot(kind="bar", stacked=True)
        else:  # bar
            pivot.plot(kind="bar")
        plt.ylabel("Total Spend ($)")
        plt.tight_layout()
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze credit card spending with flexible dimensions")
    parser.add_argument(
        "--csv",
        default="credit_card_statements.csv",
        help="Path to credit_card_statements.csv",
    )
    parser.add_argument(
        "--dimensions",
        nargs="+",
        default=["month"],
        choices=["day", "month", "quarter", "year", "category", "merchant"],
        help="Dimensions to group by",
    )
    parser.add_argument(
        "--min-transaction",
        type=float,
        default=None,
        help="Filter out transactions below this amount",
    )
    parser.add_argument(
        "--max-transaction",
        type=float,
        default=None,
        help="Filter out transactions above this amount",
    )
    parser.add_argument(
        "--min-total",
        type=float,
        default=None,
        help="Only display groups with totals above this amount",
    )
    parser.add_argument(
        "--chart-type",
        default="bar",
        choices=["bar", "pie", "stacked"],
        help="Type of chart to display",
    )
    args = parser.parse_args()

    df = load_data(args.csv)
    df = filter_transactions(df, args.min_transaction, args.max_transaction)
    summary = aggregate_spending(df, args.dimensions, args.min_total)
    display(summary, args.dimensions, args.chart_type)


if __name__ == "__main__":
    main()
