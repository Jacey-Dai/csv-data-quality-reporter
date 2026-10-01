"""Unit tests for data-quality analysis and formatting."""

import pandas as pd

from reporter import (
    analyze_dataframe,
    dataset_shape,
    duplicate_count,
    find_outliers,
    format_report,
    missing_values,
    numeric_summary,
)


def test_basic_shape_missing_and_duplicates():
    df = pd.DataFrame({"name": ["A", "A", "B"], "value": [1.0, 1.0, None]})

    assert dataset_shape(df) == {"rows": 3, "columns": 2}
    assert missing_values(df) == {"name": 0, "value": 1}
    assert duplicate_count(df) == 1


def test_numeric_summary_returns_testable_structure():
    df = pd.DataFrame({"value": [1, 2, 3]})
    summary = numeric_summary(df)

    assert summary is not None
    assert summary["value"]["count"] == 3.0
    assert summary["value"]["mean"] == 2.0


def test_iqr_detects_outlier():
    df = pd.DataFrame({"value": [10, 11, 12, 13, 14, 100]})
    result = find_outliers(df)

    assert result is not None
    assert result["value"]["count"] == 1
    assert result["value"]["values"] == [100]


def test_constant_numeric_column_has_zero_outliers():
    df = pd.DataFrame({"constant": [5, 5, 5, 5]})
    result = find_outliers(df)

    assert result["constant"]["count"] == 0


def test_missing_numeric_values_are_not_outliers():
    df = pd.DataFrame({"value": [1.0, 2.0, None, 3.0]})
    result = find_outliers(df)

    assert result["value"]["count"] == 0
    assert result["value"]["values"] == []


def test_all_missing_numeric_column_does_not_crash():
    df = pd.DataFrame({"all_missing": pd.Series([None, None], dtype="float64")})
    result = find_outliers(df)

    assert result["all_missing"]["count"] == 0
    assert result["all_missing"]["iqr"] is None
    assert numeric_summary(df)["all_missing"]["count"] == 0.0


def test_text_only_skips_numeric_analysis_clearly():
    df = pd.DataFrame({"name": ["Alice", "Bob"], "city": ["Durham", "Raleigh"]})
    analysis = analyze_dataframe(df)
    report = format_report(analysis)

    assert analysis["numeric_summary"] is None
    assert analysis["outliers"] is None
    assert report.count("Skipped: No numeric columns were found.") == 2


def test_header_only_dataframe_generates_report():
    df = pd.DataFrame(columns=["name", "age"])
    analysis = analyze_dataframe(df)
    report = format_report(analysis)

    assert analysis["shape"] == {"rows": 0, "columns": 2}
    assert "Rows: 0" in report
