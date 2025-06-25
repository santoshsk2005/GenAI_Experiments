import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_data(csv_path: str) -> pd.DataFrame:
    """Load the credit card statement CSV."""
    df = pd.read_csv(
        csv_path,
        parse_dates=["Transaction Date", "Posting Date"],
    )
    df["Amount"] = df["Amount"].astype(float)
    df["Month"] = df["Transaction Date"].dt.to_period("M").astype(str)
    return df


def aggregate_spending(df: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    """Aggregate spending along the requested dimensions."""
    available_dims = {"month": "Month", "category": "Category"}
    cols = [available_dims[d] for d in dimensions]
    summary = df.groupby(cols)["Amount"].sum().reset_index()
    return summary


def display(summary: pd.DataFrame, dimensions: list[str]) -> None:
    """Pretty-print the summary and plot a simple chart."""
    print("\nSpending Summary:\n")
    print(summary.to_string(index=False))

    # Basic bar chart for a quick visual
    if len(dimensions) == 1:
        summary.plot.bar(x=dimensions[0], y="Amount", legend=False)
        plt.ylabel("Total Spend ($)")
        plt.tight_layout()
        plt.show()
    elif len(dimensions) == 2:
        pivot = summary.pivot(index=dimensions[0], columns=dimensions[1], values="Amount")
        pivot.plot(kind="bar", stacked=True)
        plt.ylabel("Total Spend ($)")
        plt.tight_layout()
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze credit card spending")
    parser.add_argument(
        "--csv",
        default="credit_card_statements.csv",
        help="Path to credit_card_statements.csv",
    )
    parser.add_argument(
        "--dimensions",
        nargs="+",
        default=["month"],
        choices=["month", "category"],
        help="Dimensions to group by (month, category)",
    )
    args = parser.parse_args()

    df = load_data(args.csv)
    summary = aggregate_spending(df, args.dimensions)
    display(summary, args.dimensions)


if __name__ == "__main__":
    main()
