# CSV Data Quality Reporter

**Student:** Zhenmin Dai  
**NetID:** zd86  
**Project:** IDS 706 — Option 3: CSV Data Quality Reporter

A beginner-friendly command-line program that uses pandas to inspect a CSV file and print a compact data-quality report.

## Features

The report includes dataset dimensions, pandas column data types, missing-value counts and percentages, duplicate-row count and percentage, numeric summary statistics, and numeric outliers detected with the IQR method.

For each usable numeric column, the program calculates and displays `Q1`, `Q3`, `IQR = Q3 - Q1`, the lower bound `Q1 - 1.5 * IQR`, the upper bound `Q3 + 1.5 * IQR`, and the outlier count. Outlier values are shown when any exist. Missing numeric values are ignored during quartile and outlier calculations.

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

Show CLI help:

```bash
python main.py --help
```

A successful analysis exits with status code 0. Expected input/read failures print a clear message to stderr and return a nonzero status instead of printing a traceback.

## Understanding the output

- **Dataset Dimensions** shows row and column counts.
- **Column Data Types** shows the pandas dtype inferred for each column.
- **Missing Values** shows the missing-value count and percentage for every column.
- **Duplicate Rows** shows the duplicate-row count and percentage, where duplicates are rows repeated after their first occurrence.
- **Numeric Summary Statistics** reports pandas descriptive statistics for numeric columns.
- **Numeric Outliers — IQR Method** reports Q1, Q3, IQR, lower bound, upper bound, and outlier count for each usable numeric column. Outlier values are also listed when any exist.

The included `data/sample.csv` contains text and numeric columns, missing data, a duplicate row, and an age value that is detected as an IQR outlier.

## Edge-case behavior

- A missing file produces a clear error and a nonzero exit code.
- A directory supplied as the input produces a clear error and a nonzero exit code.
- A zero-byte/no-column CSV produces a clear error and a nonzero exit code.
- Permission, parsing, and text-decoding errors are reported without an expected traceback.
- A header-only CSV is valid and produces a report with zero rows and `0.00%` missing/duplicate percentages.
- A text-only CSV produces the general report and clearly skips numeric summaries and IQR analysis.
- Constant numeric columns are valid and have zero IQR outliers.
- Missing numeric values are ignored during IQR analysis.
- All-missing numeric columns are handled without crashing and report that no non-missing values are available for IQR calculation.

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

## Known Limitations

- The program accepts CSV files only.
- Column types depend on pandas dtype inference; mixed numeric/text columns may be treated as text and skipped by numeric analysis.
- Custom missing-value markers such as `unknown` are not automatically treated as missing unless pandas recognizes them as missing values.
- IQR outliers are statistical flags, not proof that a record is incorrect.
- Very large CSV files are loaded fully into memory because the project intentionally uses a simple pandas workflow.

## Manual smoke test

After installing dependencies, run the following checks from the project root.

1. Confirm the CLI help works:

   ```bash
   python main.py --help
   ```

2. Run the included sample and valid edge cases:

   ```bash
   python main.py data/sample.csv
   python main.py tests/fixtures/header_only.csv
   python main.py tests/fixtures/text_only.csv
   ```

3. Confirm a missing file fails cleanly:

   ```bash
   python main.py does-not-exist.csv
   ```

4. Confirm a zero-byte CSV fails cleanly:

   ```bash
   touch /tmp/empty.csv
   python main.py /tmp/empty.csv
   ```

5. Run the complete automated test suite:

   ```bash
   python -m pytest -v
   ```

6. If Docker is installed, build and run the default container:

   ```bash
   docker build -t csv-data-quality-reporter .
   docker run --rm csv-data-quality-reporter
   ```

7. If Docker is installed, verify a mounted CSV:

   ```bash
   docker run --rm \
     -v "$(pwd)/data/sample.csv:/app/input.csv:ro" \
     csv-data-quality-reporter /app/input.csv
   ```

For valid CSV files, confirm the command exits successfully and prints the report. For invalid inputs, confirm the command returns a nonzero status, writes the error to stderr, leaves stdout empty, and does not show a traceback.
