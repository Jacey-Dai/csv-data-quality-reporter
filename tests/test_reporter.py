"""Unit tests for data-quality analysis and formatting."""

import pandas as pd
import pytest

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
    assert missing_values(df) == {
        "name": {"count": 0, "percentage": 0.0},
        "value": {"count": 1, "percentage": pytest.approx(100 / 3)},
    }
    assert duplicate_count(df) == {
        "count": 1,
        "percentage": pytest.approx(100 / 3),
    }


def test_zero_row_percentages_are_zero():
    df = pd.DataFrame(columns=["name", "value"])

    assert missing_values(df) == {
        "name": {"count": 0, "percentage": 0.0},
        "value": {"count": 0, "percentage": 0.0},
    }
    assert duplicate_count(df) == {"count": 0, "percentage": 0.0}


def test_numeric_summary_returns_testable_structure():
    df = pd.DataFrame({"value": [1, 2, 3]})
    summary = numeric_summary(df)

    assert summary is not None
    assert summary["value"]["count"] == 3.0
    assert summary["value"]["mean"] == 2.0


def test_iqr_detects_outlier_with_exact_statistics():
    df = pd.DataFrame({"value": [10, 11, 12, 13, 14, 100]})
    result = find_outliers(df)

    assert result is not None
    value_result = result["value"]
    assert value_result["q1"] == pytest.approx(11.25)
    assert value_result["q3"] == pytest.approx(13.75)
    assert value_result["iqr"] == pytest.approx(2.5)
    assert value_result["lower_bound"] == pytest.approx(7.5)
    assert value_result["upper_bound"] == pytest.approx(17.5)
    assert value_result["count"] == 1
    assert value_result["values"] == [100]


def test_constant_numeric_column_has_zero_outliers():
    df = pd.DataFrame({"constant": [5, 5, 5, 5]})
    result = find_outliers(df)

    assert result["constant"]["q1"] == 5.0
    assert result["constant"]["q3"] == 5.0
    assert result["constant"]["iqr"] == 0.0
    assert result["constant"]["lower_bound"] == 5.0
    assert result["constant"]["upper_bound"] == 5.0
    assert result["constant"]["count"] == 0


def test_missing_numeric_values_are_excluded_from_iqr_calculation():
    df = pd.DataFrame({"value": [1.0, 2.0, None, 3.0, 4.0, 100.0]})
    result = find_outliers(df)

    value_result = result["value"]
    assert value_result["q1"] == pytest.approx(2.0)
    assert value_result["q3"] == pytest.approx(4.0)
    assert value_result["iqr"] == pytest.approx(2.0)
    assert value_result["lower_bound"] == pytest.approx(-1.0)
    assert value_result["upper_bound"] == pytest.approx(7.0)
    assert value_result["count"] == 1
    assert value_result["values"] == [100.0]


def test_all_missing_numeric_column_does_not_crash():
    df = pd.DataFrame({"all_missing": pd.Series([None, None], dtype="float64")})
    result = find_outliers(df)
    report = format_report(analyze_dataframe(df))

    assert result["all_missing"]["count"] == 0
    assert result["all_missing"]["iqr"] is None
    assert numeric_summary(df)["all_missing"]["count"] == 0.0
    assert "No non-missing values available for IQR calculation." in report


def test_text_only_skips_numeric_analysis_clearly():
    df = pd.DataFrame({"name": ["Alice", "Bob"], "city": ["Durham", "Raleigh"]})
    analysis = analyze_dataframe(df)
    report = format_report(analysis)

    assert analysis["numeric_summary"] is None
    assert analysis["outliers"] is None
    assert report.count("Skipped: No numeric columns were found.") == 2


def test_header_only_dataframe_generates_report_with_zero_percentages():
    df = pd.DataFrame(columns=["name", "age"])
    analysis = analyze_dataframe(df)
    report = format_report(analysis)

    assert analysis["shape"] == {"rows": 0, "columns": 2}
    assert "Rows: 0" in report
    assert "Columns: 2" in report
    assert "name: 0 (0.00%)" in report
    assert "age: 0 (0.00%)" in report
    assert "Count: 0" in report
    assert "Percentage: 0.00%" in report
