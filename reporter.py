"""Data-quality analysis and report formatting for CSV files."""

from __future__ import annotations

import pandas as pd


def dataset_shape(df: pd.DataFrame) -> dict[str, int]:
    """Return the number of rows and columns in a DataFrame."""
    rows, columns = df.shape
    return {"rows": rows, "columns": columns}


def column_types(df: pd.DataFrame) -> dict[str, str]:
    """Return each column name and its pandas data type."""
    return {column: str(dtype) for column, dtype in df.dtypes.items()}


def missing_values(df: pd.DataFrame) -> dict[str, int]:
    """Return the number of missing values in each column."""
    return {column: int(count) for column, count in df.isna().sum().items()}


def duplicate_count(df: pd.DataFrame) -> int:
    """Return the number of duplicate rows."""
    return int(df.duplicated().sum())


def numeric_summary(df: pd.DataFrame) -> dict[str, dict[str, float]] | None:
    """Return summary statistics for numeric columns, or None if none exist."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] == 0:
        return None

    summary = numeric_df.describe().to_dict()
    return {
        column: {statistic: float(value) for statistic, value in statistics.items()}
        for column, statistics in summary.items()
    }


def find_outliers(df: pd.DataFrame) -> dict[str, dict[str, object]] | None:
    """Find numeric outliers using the 1.5 * IQR rule.

    Missing values are ignored. Columns with no non-missing numeric values return
    zero outliers and None for quartile/bound values.
    """
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] == 0:
        return None

    results: dict[str, dict[str, object]] = {}

    for column in numeric_df.columns:
        values = numeric_df[column].dropna()

        if values.empty:
            results[column] = {
                "q1": None,
                "q3": None,
                "iqr": None,
                "lower_bound": None,
                "upper_bound": None,
                "count": 0,
                "values": [],
            }
            continue

        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = values[(values < lower_bound) | (values > upper_bound)]

        results[column] = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "count": int(outliers.shape[0]),
            "values": outliers.tolist(),
        }

    return results


def analyze_dataframe(df: pd.DataFrame) -> dict[str, object]:
    """Run all data-quality checks and return testable analysis results."""
    return {
        "shape": dataset_shape(df),
        "column_types": column_types(df),
        "missing_values": missing_values(df),
        "duplicate_rows": duplicate_count(df),
        "numeric_summary": numeric_summary(df),
        "outliers": find_outliers(df),
    }


def _format_number(value: float) -> str:
    """Format a numeric result compactly for terminal output."""
    return f"{value:.4g}"


def format_report(analysis: dict[str, object]) -> str:
    """Convert analysis results into a human-readable terminal report."""
    shape = analysis["shape"]
    types = analysis["column_types"]
    missing = analysis["missing_values"]
    summary = analysis["numeric_summary"]
    outliers = analysis["outliers"]

    lines = [
        "CSV Data Quality Report",
        "=======================",
        "",
        "Dataset Shape",
        "-------------",
        f"Rows: {shape['rows']}",
        f"Columns: {shape['columns']}",
        "",
        "Column Data Types",
        "-----------------",
    ]

    if types:
        lines.extend(f"{column}: {dtype}" for column, dtype in types.items())
    else:
        lines.append("No columns found.")

    lines.extend(["", "Missing Values", "--------------"])
    if missing:
        lines.extend(f"{column}: {count}" for column, count in missing.items())
    else:
        lines.append("No columns found.")

    lines.extend(
        [
            "",
            "Duplicate Rows",
            "--------------",
            str(analysis["duplicate_rows"]),
            "",
            "Numeric Summary",
            "---------------",
        ]
    )

    if summary is None:
        lines.append("Skipped: No numeric columns were found.")
    else:
        for column, statistics in summary.items():
            lines.append(f"{column}:")
            for statistic, value in statistics.items():
                lines.append(f"  {statistic}: {_format_number(value)}")

    lines.extend(["", "IQR Outliers", "------------"])
    if outliers is None:
        lines.append("Skipped: No numeric columns were found.")
    else:
        for column, result in outliers.items():
            lines.append(f"{column}:")
            lines.append(f"  Outlier count: {result['count']}")
            if result["values"]:
                lines.append(f"  Outlier values: {result['values']}")
            elif result["iqr"] is None:
                lines.append("  No non-missing values available for IQR calculation.")

    return "\n".join(lines)
