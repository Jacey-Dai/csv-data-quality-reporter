"""Command-line interface for the CSV Data Quality Reporter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from reporter import analyze_dataframe, format_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze a CSV file and print a data-quality report."
    )
    parser.add_argument("csv_file", help="Path to the CSV file to analyze")
    return parser.parse_args(argv)


def load_csv(file_path: str) -> pd.DataFrame:
    """Validate the input path and load a CSV file with pandas."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(file_path)
    if path.is_dir():
        raise IsADirectoryError(file_path)

    return pd.read_csv(path)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return 0 on success or a nonzero status on failure."""
    args = parse_args(argv)

    try:
        df = load_csv(args.csv_file)
    except FileNotFoundError:
        print(f"Error: File '{args.csv_file}' does not exist.", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"Error: '{args.csv_file}' is a directory, not a CSV file.", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: Permission denied when reading '{args.csv_file}'.", file=sys.stderr)
        return 1
    except pd.errors.EmptyDataError:
        print(
            f"Error: '{args.csv_file}' is empty or contains no CSV columns.",
            file=sys.stderr,
        )
        return 1
    except pd.errors.ParserError:
        print(f"Error: Could not parse '{args.csv_file}' as CSV.", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(
            f"Error: Could not decode '{args.csv_file}' as a text CSV file.",
            file=sys.stderr,
        )
        return 1

    analysis = analyze_dataframe(df)
    print(format_report(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
