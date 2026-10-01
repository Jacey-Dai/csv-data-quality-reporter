"""Integration tests for the command-line interface."""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN = PROJECT_ROOT / "main.py"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"
REQUIRED_SECTIONS = [
    "Dataset Dimensions",
    "Column Data Types",
    "Missing Values",
    "Duplicate Rows",
    "Numeric Summary Statistics",
    "Numeric Outliers — IQR Method",
]


def run_cli(path: Path) -> subprocess.CompletedProcess[str]:
    """Run the CLI with the same Python interpreter used by pytest."""
    return subprocess.run(
        [sys.executable, str(MAIN), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_successful_cli_returns_zero_and_all_sections():
    result = run_cli(PROJECT_ROOT / "data" / "sample.csv")

    assert result.returncode == 0
    assert "CSV Data Quality Report" in result.stdout
    for section in REQUIRED_SECTIONS:
        assert section in result.stdout
    assert result.stderr == ""


def test_missing_file_returns_nonzero_stderr_only_without_traceback(tmp_path):
    result = run_cli(tmp_path / "missing.csv")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "does not exist" in result.stderr
    assert "Traceback" not in result.stderr


def test_directory_returns_nonzero_stderr_only_without_traceback(tmp_path):
    result = run_cli(tmp_path)

    assert result.returncode != 0
    assert result.stdout == ""
    assert "is a directory" in result.stderr
    assert "Traceback" not in result.stderr


def test_zero_byte_csv_returns_nonzero_stderr_only_without_traceback(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()
    result = run_cli(empty_file)

    assert result.returncode != 0
    assert result.stdout == ""
    assert "empty or contains no CSV columns" in result.stderr
    assert "Traceback" not in result.stderr


def test_header_only_csv_returns_zero_with_dimensions_and_percentages():
    result = run_cli(FIXTURES / "header_only.csv")

    assert result.returncode == 0
    assert "Rows: 0" in result.stdout
    assert "Columns: 3" in result.stdout
    assert "name: 0 (0.00%)" in result.stdout
    assert "age: 0 (0.00%)" in result.stdout
    assert "score: 0 (0.00%)" in result.stdout
    assert "Percentage: 0.00%" in result.stdout
    assert result.stderr == ""
    assert "Traceback" not in result.stdout


def test_text_only_csv_returns_zero_and_skips_numeric_sections():
    result = run_cli(FIXTURES / "text_only.csv")

    assert result.returncode == 0
    assert result.stdout.count("Skipped: No numeric columns were found.") == 2
    assert result.stderr == ""


def test_constant_numeric_csv_works_through_cli(tmp_path):
    csv_file = tmp_path / "constant.csv"
    csv_file.write_text("value\n5\n5\n5\n5\n", encoding="utf-8")

    result = run_cli(csv_file)

    assert result.returncode == 0
    assert "Q1: 5" in result.stdout
    assert "Q3: 5" in result.stdout
    assert "IQR: 0" in result.stdout
    assert "Lower bound: 5" in result.stdout
    assert "Upper bound: 5" in result.stdout
    assert "Outlier count: 0" in result.stdout
    assert result.stderr == ""


def test_numeric_with_missing_values_works_through_cli(tmp_path):
    csv_file = tmp_path / "missing_numeric.csv"
    csv_file.write_text(
        "value,label\n1,a\n2,b\n,c\n3,d\n4,e\n100,f\n",
        encoding="utf-8",
    )

    result = run_cli(csv_file)

    assert result.returncode == 0
    assert "value: 1 (16.67%)" in result.stdout
    assert "Q1: 2" in result.stdout
    assert "Q3: 4" in result.stdout
    assert "Lower bound: -1" in result.stdout
    assert "Upper bound: 7" in result.stdout
    assert "Outlier count: 1" in result.stdout
    assert "Outlier values: [100.0]" in result.stdout
    assert result.stderr == ""


def test_all_missing_numeric_csv_works_through_cli(tmp_path):
    csv_file = tmp_path / "all_missing_numeric.csv"
    csv_file.write_text("value,label\n,a\n,b\n,c\n", encoding="utf-8")

    result = run_cli(csv_file)

    assert result.returncode == 0
    assert "value: 3 (100.00%)" in result.stdout
    assert "No non-missing values available for IQR calculation." in result.stdout
    assert "Outlier count: 0" in result.stdout
    assert result.stderr == ""
