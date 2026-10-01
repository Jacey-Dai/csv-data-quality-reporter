# CSV Data Quality Reporter

**Student:** Zhenmin Dai  
**NetID:** zd86  
**Project:** IDS 706 — Option 3: CSV Data Quality Reporter

A beginner-friendly command-line program that uses pandas to inspect a CSV file and print a compact data-quality report.

## Features

The report includes dataset shape, pandas column data types, missing-value counts, duplicate-row count, numeric summary statistics, and numeric outliers detected with the IQR method.

For each numeric column, the program calculates `IQR = Q3 - Q1`. Values below `Q1 - 1.5 * IQR` or above `Q3 + 1.5 * IQR` are reported as outliers. Missing numeric values are ignored during this calculation.

## Project structure

```text
main.py                     # argparse CLI, input validation, CSV loading
reporter.py                 # analysis functions and report formatting
data/sample.csv             # demonstration dataset
requirements.txt
tests/test_reporter.py      # unit tests
tests/test_cli.py           # CLI integration tests
tests/fixtures/             # small edge-case CSV files
Dockerfile
.dockerignore
.gitignore
```

The application code intentionally stays in only `main.py` and `reporter.py`.

## Local setup

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the virtual environment with `.venv\Scripts\activate`.

## CLI usage

Analyze the included sample:

```bash
python main.py data/sample.csv
```

Analyze another CSV:

```bash
python main.py path/to/file.csv
```

A successful analysis exits with status code 0. Expected input/read failures print a clear message to stderr and return a nonzero status instead of printing a traceback.

## Understanding the output

- **Dataset Shape** shows row and column counts.
- **Column Data Types** shows the pandas dtype inferred for each column.
- **Missing Values** counts missing entries by column.
- **Duplicate Rows** counts rows duplicated after their first occurrence.
- **Numeric Summary** reports pandas descriptive statistics for numeric columns.
- **IQR Outliers** reports the count and values outside the 1.5-IQR bounds.

The included `data/sample.csv` contains text and numeric columns, missing data, a duplicate row, and an age value that is detected as an IQR outlier.

## Edge-case behavior

- A missing file produces a clear error and a nonzero exit code.
- A directory supplied as the input produces a clear error and a nonzero exit code.
- A zero-byte/no-column CSV produces a clear error and a nonzero exit code.
- Permission, parsing, and text-decoding errors are reported without an expected traceback.
- A header-only CSV is valid and produces a report with zero rows.
- A text-only CSV produces the general report and clearly skips numeric summaries and IQR analysis.
- Constant numeric columns are valid and have zero IQR outliers.
- Missing numeric values are ignored during IQR analysis.
- All-missing numeric columns are handled without crashing.

## Tests

Run all unit and CLI integration tests from the project root:

```bash
python -m pytest -v
```

The CLI tests use `sys.executable`, so subprocess tests use the same Python interpreter that runs pytest.

## Docker

Build the image:

```bash
docker build -t csv-data-quality-reporter .
```

Run it with the included sample CSV (the Dockerfile's default command):

```bash
docker run --rm csv-data-quality-reporter
```

The Dockerfile uses:

```dockerfile
ENTRYPOINT ["python", "main.py"]
CMD ["data/sample.csv"]
```

To analyze a CSV from the current host directory, mount it read-only and pass its container path as the argument:

```bash
docker run --rm \
  -v "$(pwd)/my_data.csv:/app/input.csv:ro" \
  csv-data-quality-reporter /app/input.csv
```

## Manual smoke test

After installing dependencies, run:

```bash
python main.py data/sample.csv
python main.py tests/fixtures/header_only.csv
python main.py tests/fixtures/text_only.csv
python main.py does-not-exist.csv
```

Confirm that the first three commands produce reports, while the missing-file command prints a clear error to stderr and returns a nonzero exit status.
