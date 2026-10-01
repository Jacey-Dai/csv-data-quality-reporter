"""Integration tests for the command-line interface."""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN = PROJECT_ROOT / "main.py"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def run_cli(path: Path) -> subprocess.CompletedProcess[str]:
    """Run the CLI with the same Python interpreter used by pytest."""
    return subprocess.run(
        [sys.executable, str(MAIN), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_successful_cli_returns_zero():
    result = run_cli(PROJECT_ROOT / "data" / "sample.csv")

    assert result.returncode == 0
    assert "CSV Data Quality Report" in result.stdout
    assert "Traceback" not in result.stderr


def test_missing_file_returns_nonzero_without_traceback(tmp_path):
    result = run_cli(tmp_path / "missing.csv")

    assert result.returncode != 0
    assert "does not exist" in result.stderr
    assert "Traceback" not in result.stderr


def test_directory_returns_nonzero_without_traceback(tmp_path):
    result = run_cli(tmp_path)

    assert result.returncode != 0
    assert "is a directory" in result.stderr
    assert "Traceback" not in result.stderr


def test_zero_byte_csv_returns_nonzero_without_traceback(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()
    result = run_cli(empty_file)

    assert result.returncode != 0
    assert "empty or contains no CSV columns" in result.stderr
    assert "Traceback" not in result.stderr


def test_header_only_csv_returns_zero():
    result = run_cli(FIXTURES / "header_only.csv")

    assert result.returncode == 0
    assert "Rows: 0" in result.stdout
    assert "Traceback" not in result.stderr


def test_text_only_csv_returns_zero_and_skips_numeric_sections():
    result = run_cli(FIXTURES / "text_only.csv")

    assert result.returncode == 0
    assert result.stdout.count("Skipped: No numeric columns were found.") == 2
    assert "Traceback" not in result.stderr
