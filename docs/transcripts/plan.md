# CSV Data Quality Reporter — Implementation Plan

## 1. Project Goal

Build a beginner-friendly Python command-line application that accepts a user-provided CSV file and prints a concise data-quality report.

The project should demonstrate practical software-engineering skills without unnecessary complexity. It should be easy to explain, test, run locally, and run in Docker.

The report must include:

- dataset dimensions;
- column data types;
- missing values;
- duplicate rows;
- numeric summary statistics;
- numeric outliers detected using the IQR method.

The project should not modify the input CSV. It only analyzes and reports.

---

## 2. Design Principles

The implementation should follow these principles:

- Keep the architecture simple and beginner-friendly.
- Use a small number of Python files with clear responsibilities.
- Prefer plain functions over classes.
- Use `pandas` for CSV loading and analysis.
- Use Python's built-in `argparse` module for the CLI.
- Separate data analysis from report formatting.
- Handle expected user errors with clear messages instead of tracebacks.
- Keep dependencies minimal.
- Avoid frameworks, databases, web interfaces, configuration systems, plugin systems, and unnecessary abstraction.

The main program flow should be:

```text
CSV path from user
        ↓
parse command-line argument
        ↓
load CSV
        ↓
analyze DataFrame
        ↓
format report
        ↓
print report
```

---

## 3. Functional Requirements

### 3.1 CSV Input

The program must accept one required positional command-line argument representing the CSV file path.

Expected usage:

```bash
python main.py data/sample.csv
```

The program must:

- verify that the supplied path exists;
- verify that it refers to a file rather than a directory;
- attempt to load the file with `pandas.read_csv`;
- produce a clear error if the file cannot be loaded.

The first version should support CSV files only.

It should not support:

- Excel files;
- databases;
- URLs;
- JSON input;
- automatic file-type detection.

---

## 3.2 Dataset Dimensions

The report must display:

- number of rows;
- number of columns.

Use:

```python
df.shape
```

Example report section:

```text
Dataset Dimensions
------------------
Rows: 1000
Columns: 12
```

---

## 3.3 Column Data Types

The report must display the pandas-inferred data type for every column.

Example:

```text
Column Data Types
-----------------
customer_id    int64
age            float64
state          object
active         bool
```

The program should report pandas' inferred types rather than aggressively converting data.

Automatic type coercion is out of scope.

---

## 3.4 Missing Values

For each column, report:

- missing-value count;
- missing-value percentage.

Use pandas missing-value behavior based on:

```python
df.isna()
```

Example:

```text
Missing Values
--------------
age       5    2.50%
state     0    0.00%
income   10    5.00%
```

The program should not create custom rules that automatically treat values such as:

```text
unknown
missing
not available
```

as missing.

Use pandas' standard CSV parsing behavior.

If the DataFrame contains zero rows, missing-value percentages should be reported as `0.00%` rather than attempting division by zero.

---

## 3.5 Duplicate Rows

The program must count duplicate rows using:

```python
df.duplicated().sum()
```

A duplicate row is a row whose values across all columns match a previously occurring row according to pandas' duplicate-detection behavior.

The report should include:

- duplicate row count;
- duplicate row percentage.

Example:

```text
Duplicate Rows
--------------
Duplicate rows: 4
Duplicate percentage: 1.25%
```

For a zero-row dataset:

```text
Duplicate rows: 0
Duplicate percentage: 0.00%
```

The program must only report duplicates. It must not remove them.

---

## 3.6 Numeric Summary Statistics

The program should select numeric columns using pandas, for example:

```python
df.select_dtypes(include="number")
```

For numeric columns, report standard descriptive statistics including:

- count;
- mean;
- standard deviation;
- minimum;
- 25th percentile;
- median;
- 75th percentile;
- maximum.

Using pandas `describe()` is appropriate.

Example section:

```text
Numeric Summary Statistics
--------------------------
             age        income
count      100.00        98.00
mean        34.50     62000.00
std         10.20     15000.00
min         18.00     25000.00
25%         27.00     51000.00
50%         34.00     61000.00
75%         42.00     72000.00
max         79.00    130000.00
```

The program does not need custom statistical formulas for standard descriptive statistics.

---

## 3.7 Numeric Outlier Detection

The program must detect numeric outliers using the IQR method.

For each numeric column:

```text
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
lower bound = Q1 - 1.5 × IQR
upper bound = Q3 + 1.5 × IQR
```

A non-missing value is an outlier if:

```text
value < lower bound
```

or:

```text
value > upper bound
```

Missing values must be ignored during outlier detection.

For each numeric column, report:

- Q1;
- Q3;
- IQR;
- lower bound;
- upper bound;
- outlier count.

Example:

```text
Numeric Outliers — IQR Method
-----------------------------
age
  Q1: 27.00
  Q3: 42.00
  IQR: 15.00
  Lower bound: 4.50
  Upper bound: 64.50
  Outliers: 3
```

The program should not remove, replace, cap, or otherwise modify outliers.

The report should describe them as statistical outliers, not as errors.

---

## 4. Required Edge-Case Behavior

### 4.1 Missing Input File

Example:

```bash
python main.py data/does_not_exist.csv
```

Required behavior:

- print a clear error message;
- do not display a normal Python traceback for this expected error;
- exit with a nonzero exit code.

Recommended message:

```text
Error: File not found: data/does_not_exist.csv
```

---

## 4.2 Directory Supplied Instead of File

If the user supplies a directory path instead of a CSV file, the program should:

- print a clear error;
- exit nonzero.

Example:

```text
Error: Input path is not a file: data/
```

---

## 4.3 Completely Empty CSV File

A zero-byte CSV file or a file containing no readable CSV data should not cause an uncaught pandas traceback.

If pandas raises an error such as `EmptyDataError`, the program should convert it into a short user-facing message.

Recommended output:

```text
Error: CSV file contains no readable data.
```

The program should exit with a nonzero status.

---

## 4.4 Header-Only CSV

A CSV containing column headers but no data rows should be treated as a valid empty dataset.

Example:

```csv
name,age,state
```

Expected behavior:

```text
Rows: 0
Columns: 3
```

The program should still report:

- column data types;
- missing-value counts;
- duplicate count.

Missing percentages should be:

```text
0.00%
```

Duplicate count should be:

```text
0
```

Numeric analysis should not fail.

If there is no usable numeric data, display a clear message such as:

```text
No numeric data available.
```

---

## 4.5 CSV Containing Only Text Columns

Example:

```csv
name,state,status
Alice,NC,active
Bob,WA,inactive
Carol,IL,active
```

This must be treated as a valid dataset.

The program should still report:

- dimensions;
- column data types;
- missing values;
- duplicate rows.

For numeric sections, print clear messages instead of failing.

Recommended output:

```text
Numeric Summary Statistics
--------------------------
No numeric columns found.

Numeric Outliers — IQR Method
-----------------------------
No numeric columns found.
```

---

## 4.6 Constant Numeric Column

Example:

```text
5, 5, 5, 5, 5
```

Then:

```text
Q1 = 5
Q3 = 5
IQR = 0
```

Expected result:

```text
Outliers: 0
```

The program must not incorrectly classify all values as outliers.

---

## 4.7 Numeric Column With Missing Values

Example:

```text
1, 2, NaN, 3, 4, 100
```

Missing values must be ignored when computing:

- Q1;
- Q3;
- IQR;
- bounds;
- outlier count.

Missing values themselves must not count as outliers.

---

## 4.8 All-Missing Numeric Data

If a numeric column contains no non-missing values, the program should not attempt meaningful IQR calculations.

It should return a clear result such as:

```text
No non-missing numeric values available for outlier detection.
```

The implementation should handle this without crashing.

---

## 4.9 Mixed-Type Columns

A column such as:

```text
1
2
three
4
```

may be interpreted by pandas as a text/object column.

The program should respect pandas' inferred type and should not force the column to numeric.

It should therefore be excluded from numeric summaries and IQR analysis.

---

## 5. Non-Functional Requirements

### 5.1 Readability

Code should use:

- descriptive function names;
- short functions;
- clear variable names;
- limited nesting;
- minimal duplicated logic;
- brief docstrings where useful.

Avoid unnecessarily clever code.

---

### 5.2 Simplicity

The project should remain understandable to a graduate student learning software engineering.

Do not introduce:

- custom class hierarchies;
- dependency injection;
- configuration frameworks;
- web frameworks;
- databases;
- asynchronous programming;
- plugin systems;
- unnecessary design patterns.

---

### 5.3 Reliability

Expected input errors should produce understandable messages.

The application should handle required edge cases without unexpected crashes.

---

### 5.4 Testability

Analysis functions should return structured results rather than directly printing everything.

This allows unit tests to validate calculations independently of text formatting.

---

### 5.5 Reproducibility

The project must include:

- dependency instructions;
- automated tests;
- Docker support;
- a sample CSV;
- manual smoke-test instructions.

---

## 6. Repository Structure

Use the following repository structure:

```text
csv-data-quality-reporter/
│
├── main.py
├── reporter.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── data/
│   └── sample.csv
│
├── tests/
│   ├── test_reporter.py
│   ├── test_cli.py
│   └── data/
│       └── test.csv
│
└── docs/
    └── plan.md
```

Do not create a larger package structure unless implementation later reveals a real need.

In particular, do not add folders such as:

```text
src/
services/
models/
controllers/
config/
utils/
```

for the initial version.

---

## 7. File Responsibilities

### 7.1 `main.py`

`main.py` is responsible for the command-line interface.

Responsibilities:

- create the `argparse` parser;
- accept one positional CSV file path;
- handle expected user-facing errors;
- call functions from `reporter.py`;
- print the final formatted report;
- return an appropriate exit code.

It should contain little or no statistical logic.

Conceptual flow:

```text
parse arguments
    ↓
load CSV
    ↓
analyze DataFrame
    ↓
format report
    ↓
print
```

---

## 7.2 `reporter.py`

`reporter.py` contains the core analysis and formatting logic.

Use approximately four main functions.

### `load_csv(path)`

Responsibilities:

- validate that the path exists;
- validate that the path is a file;
- load it using `pandas.read_csv`;
- translate expected CSV-loading errors into clear application-level errors.

It should return a pandas DataFrame on success.

---

### `analyze_dataframe(df)`

Responsibilities:

- calculate dataset dimensions;
- collect column data types;
- calculate missing-value counts and percentages;
- calculate duplicate count and percentage;
- identify numeric columns;
- calculate numeric summary statistics;
- call `detect_iqr_outliers()` for each numeric column;
- return a structured analysis result.

The result may use dictionaries and pandas objects.

Example conceptual structure:

```text
{
    "dimensions": ...,
    "dtypes": ...,
    "missing": ...,
    "duplicates": ...,
    "numeric_summary": ...,
    "outliers": ...
}
```

Exact internal formatting may be chosen by the Builder, but the output must remain simple and testable.

---

### `detect_iqr_outliers(series)`

Responsibilities:

- remove missing values from the supplied numeric Series;
- handle an empty non-missing Series safely;
- calculate Q1;
- calculate Q3;
- calculate IQR;
- calculate lower and upper bounds;
- count values outside those bounds;
- return the calculated values in a structured form.

This function contains the main custom statistical logic and should receive focused unit tests.

---

### `format_report(results)`

Responsibilities:

- convert the structured analysis results into a readable multiline text report;
- display report sections in a predictable order;
- display special messages for skipped numeric analyses;
- perform presentation only, not statistical calculations.

---

## 8. Command-Line Interface

Use Python's standard `argparse` module.

Required usage:

```bash
python main.py <csv_file>
```

Example:

```bash
python main.py data/sample.csv
```

Help command:

```bash
python main.py --help
```

Expected structure:

```text
usage: main.py [-h] csv_file

Generate a data quality report for a CSV file.

positional arguments:
  csv_file    Path to the CSV file to analyze
```

Do not add additional CLI options in the initial version unless clearly necessary.

In particular, do not initially add:

```text
--output
--format
--config
--verbose
--threshold
--outlier-method
```

---

## 9. Report Format

The report should use a consistent section order.

Recommended format:

```text
CSV Data Quality Report
=======================

File: data/sample.csv

Dataset Dimensions
------------------
Rows: ...
Columns: ...

Column Data Types
-----------------
...

Missing Values
--------------
...

Duplicate Rows
--------------
...

Numeric Summary Statistics
--------------------------
...

Numeric Outliers — IQR Method
-----------------------------
...
```

The exact spacing may be adjusted during implementation, but section names and ordering should remain stable enough for documentation and integration testing.

---

## 10. Dependencies

Keep dependencies minimal.

Recommended `requirements.txt`:

```text
pandas
pytest
```

No additional CLI framework is needed.

Do not introduce packages such as:

```text
click
typer
rich
pydantic
flask
django
```

unless a future requirement clearly justifies them.

---

## 11. Sample Dataset

Create:

```text
data/sample.csv
```

The sample file should be small and intentionally include:

- at least one numeric column;
- at least one text column;
- at least one missing value;
- at least one duplicate row;
- at least one obvious numeric outlier.

The file should be designed so that running the application demonstrates most project features at once.

The sample data should not contain sensitive or real personal information.

---

## 12. Testing Strategy

Use `pytest`.

Testing should be divided into:

- unit tests for analysis logic;
- integration tests for the real CLI behavior.

Avoid testing pandas internals unnecessarily.

Focus tests on project behavior and custom logic.

---

## 13. Unit Tests

Place unit tests in:

```text
tests/test_reporter.py
```

Required test coverage should include the following.

### 13.1 Dataset Dimensions

Create a small DataFrame and confirm the correct row and column counts are returned.

---

### 13.2 Data Types

Confirm that reported data types correspond to the DataFrame's pandas dtypes.

---

### 13.3 Missing Values

Test a DataFrame with known missing values.

Verify:

- missing counts;
- missing percentages;
- zero-missing columns.

Also test a zero-row DataFrame to ensure percentages do not cause division-by-zero errors.

---

### 13.4 Duplicate Rows

Test:

- a DataFrame containing duplicates;
- a DataFrame with no duplicates;
- a zero-row DataFrame.

Verify correct counts and percentages.

---

### 13.5 Numeric Summary Statistics

Test a small DataFrame with numeric and text columns.

Verify that:

- numeric columns are included;
- text columns are excluded;
- expected summary-statistic fields are present.

Do not duplicate all pandas `describe()` calculations manually.

---

### 13.6 Text-Only DataFrame

Create a DataFrame containing only text columns.

Verify:

- the general analysis succeeds;
- numeric summary results indicate no numeric columns;
- outlier results indicate no numeric columns.

---

### 13.7 IQR Outlier Detection

Use a small numeric Series containing an obvious extreme value.

Example:

```text
1, 2, 2, 3, 3, 4, 100
```

Verify:

- Q1;
- Q3;
- IQR;
- lower bound;
- upper bound;
- outlier count.

This is one of the most important unit tests.

---

### 13.8 IQR With Missing Values

Example:

```text
1, 2, NaN, 3, 4, 100
```

Verify that:

- missing values are ignored;
- missing values do not count as outliers;
- the calculation does not fail.

---

### 13.9 Constant Numeric Column

Example:

```text
5, 5, 5, 5
```

Verify:

```text
IQR = 0
Outlier count = 0
```

---

### 13.10 Empty Non-Missing Numeric Series

Test a numeric Series containing only missing values.

Verify that the function returns a safe, explicit result rather than crashing.

---

## 14. Integration Tests

Place CLI integration tests in:

```text
tests/test_cli.py
```

Use `subprocess.run()` so that the tests exercise the application the way a real user would.

---

### 14.1 Successful CLI Run

Run:

```bash
python main.py tests/data/test.csv
```

Verify:

- return code is `0`;
- output contains `CSV Data Quality Report`;
- output contains `Dataset Dimensions`;
- output contains `Column Data Types`;
- output contains `Missing Values`;
- output contains `Duplicate Rows`;
- output contains `Numeric Summary Statistics`;
- output contains `Numeric Outliers`.

Do not compare the entire output character-for-character.

---

### 14.2 Missing File

Run the program with a nonexistent path.

Verify:

- return code is nonzero;
- output contains a clear file-not-found message;
- no normal traceback is shown for this expected condition.

---

### 14.3 Completely Empty CSV

Run the program using a zero-byte CSV fixture.

Verify:

- return code is nonzero;
- output contains a clear empty-file message;
- no uncaught traceback appears.

---

### 14.4 Text-Only CSV

Run the CLI on a CSV containing only text columns.

Verify:

- return code is `0`;
- general report sections appear;
- numeric summary section explains that no numeric columns were found;
- outlier section explains that no numeric columns were found.

---

### 14.5 Header-Only CSV

Run the CLI on a CSV with headers but no data rows.

Verify:

- return code is `0`;
- rows are reported as zero;
- the report completes without crashing.

---

## 15. Docker Approach

Provide:

```text
Dockerfile
.dockerignore
```

Use a small official Python image such as:

```text
python:3.12-slim
```

The Docker image should:

1. set a working directory;
2. copy dependency definitions;
3. install dependencies;
4. copy the project files;
5. run a meaningful default analysis.

The container should not simply print a placeholder message.

---

## 16. Meaningful Default Container Behavior

The default Docker command should analyze:

```text
data/sample.csv
```

Therefore:

```bash
docker run --rm csv-quality-reporter
```

should print an actual data-quality report.

This proves that the container executes the real project logic.

The exact Dockerfile syntax will be implemented later by the Builder.

---

## 17. User-Provided CSV With Docker

The README should document how to mount a local directory containing a CSV file into the container and run the program against that file.

Conceptually:

```bash
docker run --rm \
  -v "$(pwd)/data:/data" \
  csv-quality-reporter \
  python main.py /data/my_file.csv
```

The final command must be tested before being added to the README.

---

## 18. `.dockerignore`

Exclude files not needed to run the application.

Recommended entries:

```text
.git
.github
__pycache__
.pytest_cache
*.pyc
.venv
venv
```

Tests, docs, and README may also be excluded if they are not needed at runtime.

Do not exclude:

```text
data/sample.csv
```

because the default container should analyze it.

---

## 19. Manual Smoke-Test Procedure

The final README must include a manual smoke-test procedure.

The Builder should verify every command before documenting it.

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

Expected result:

- dependencies install successfully.

---

### Step 2: Check CLI help

```bash
python main.py --help
```

Expected result:

- usage instructions appear;
- the required CSV path argument is shown.

---

### Step 3: Run the sample analysis

```bash
python main.py data/sample.csv
```

Manually verify that the output includes:

- dataset dimensions;
- column data types;
- missing values;
- duplicate rows;
- numeric summaries;
- IQR-based outliers.

---

### Step 4: Test missing file behavior

```bash
python main.py does_not_exist.csv
```

Expected result:

- clear error message;
- nonzero exit code;
- no normal traceback.

---

### Step 5: Test empty-file behavior

Run the application using a completely empty CSV file.

Expected result:

- clear empty-file message;
- nonzero exit code;
- no uncaught traceback.

---

### Step 6: Run automated tests

```bash
pytest
```

Expected result:

- all tests pass.

---

### Step 7: Build the Docker image

```bash
docker build -t csv-quality-reporter .
```

Expected result:

- image builds successfully.

---

### Step 8: Run the default container analysis

```bash
docker run --rm csv-quality-reporter
```

Expected result:

- a real report is generated for `data/sample.csv`.

---

### Step 9: Test a mounted CSV

Run the documented volume-mount command against a local CSV.

Expected result:

- the container analyzes the mounted file successfully.

---

## 20. README Requirements

The final `README.md` should contain:

- project title;
- brief project description;
- feature list;
- requirements;
- setup instructions;
- command-line usage;
- example command;
- explanation of each report section;
- testing instructions;
- Docker build instructions;
- Docker run instructions;
- mounted-file Docker example;
- manual smoke-test procedure;
- brief explanation of the IQR method;
- known limitations.

All documented commands should match the actual implementation.

---

## 21. Error-Handling Strategy

Expected user errors should be handled explicitly.

The application should provide clear user-facing messages for:

- missing file;
- directory instead of file;
- completely empty CSV;
- unreadable or malformed CSV where pandas raises a parsing error.

Unexpected programming errors should not be silently swallowed.

Do not use a broad:

```python
except Exception:
```

that hides all problems without distinction.

Prefer handling expected exceptions specifically.

---

## 22. Out-of-Scope Features

The initial project should not include:

- automatic data cleaning;
- automatic removal of duplicates;
- automatic outlier removal;
- automatic type conversion;
- machine-learning-based anomaly detection;
- HTML reports;
- PDF reports;
- JSON reports;
- charts;
- web interfaces;
- APIs;
- databases;
- Excel support;
- configuration files;
- configurable outlier methods;
- plugin systems;
- parallel processing;
- advanced logging frameworks.

These may be mentioned as possible future improvements but should not be implemented in the initial version.

---

## 23. Risks and Design Concerns

### 23.1 Overengineering

Risk:

The project could become harder to explain if too many modules, classes, abstractions, or frameworks are introduced.

Decision:

Use only:

```text
main.py
reporter.py
```

for core application logic.

Use plain functions.

---

### 23.2 Mixing Analysis and Printing

Risk:

If statistical functions directly print results, unit testing becomes harder.

Decision:

Analysis functions should return results.

`format_report()` should handle presentation.

`main.py` should print the final string.

---

### 23.3 Ambiguous Missing Values

Risk:

Users may expect values such as `"unknown"` to count as missing.

Decision:

Use pandas' standard parsing and `isna()` behavior.

Do not create custom domain-specific missing-value rules.

---

### 23.4 Mixed-Type Columns

Risk:

A mostly numeric column with one text value may be inferred as nonnumeric.

Decision:

Respect pandas' inferred type.

Do not automatically coerce it.

---

### 23.5 Outlier Interpretation

Risk:

Users may assume an IQR outlier is incorrect data.

Decision:

Describe values as IQR-based statistical outliers only.

Do not label them as errors.

---

### 23.6 Fragile Output Tests

Risk:

Testing the entire formatted report as one exact string can make harmless formatting changes break tests.

Decision:

Unit-test calculation results separately.

Integration tests should check important output sections and messages rather than exact full output.

---

### 23.7 Docker Documentation Drift

Risk:

Documented Docker commands may not match the final image behavior.

Decision:

Include Docker commands in the manual smoke-test procedure and execute them before submission.

---

## 24. Implementation Order

The Builder should follow this order.

### Phase 1: Create Project Skeleton

Create:

```text
main.py
reporter.py
requirements.txt
README.md
Dockerfile
.dockerignore
.gitignore
data/
tests/
docs/
```

Add the finalized `docs/plan.md`.

---

### Phase 2: Implement CSV Loading

Implement:

```text
load_csv(path)
```

Handle:

- valid file;
- missing file;
- directory path;
- completely empty file;
- pandas parsing errors.

Add tests before moving on.

---

### Phase 3: Implement General Data Analysis

Implement the general parts of:

```text
analyze_dataframe(df)
```

Include:

- shape;
- data types;
- missing counts and percentages;
- duplicate count and percentage.

Add unit tests.

---

### Phase 4: Implement Numeric Summary Statistics

Add numeric-column selection and descriptive statistics.

Handle:

- normal numeric columns;
- text-only datasets;
- zero-row datasets.

Add tests.

---

### Phase 5: Implement IQR Outlier Detection

Implement:

```text
detect_iqr_outliers(series)
```

Test:

- normal data;
- obvious outlier;
- missing values;
- constant values;
- all-missing numeric data.

Then connect it to:

```text
analyze_dataframe(df)
```

for each numeric column.

---

### Phase 6: Implement Report Formatting

Implement:

```text
format_report(results)
```

Ensure the report includes all required sections and edge-case messages.

Do not add statistical calculations to this function.

---

### Phase 7: Implement CLI

Implement `argparse` in `main.py`.

Connect:

```text
CSV path
 → load_csv
 → analyze_dataframe
 → format_report
 → print
```

Return:

- zero exit code for successful reports;
- nonzero exit code for expected input errors.

---

### Phase 8: Add CLI Integration Tests

Test:

- normal CSV;
- missing file;
- completely empty CSV;
- text-only CSV;
- header-only CSV.

---

### Phase 9: Create Sample Dataset

Create:

```text
data/sample.csv
```

Include:

- text columns;
- numeric columns;
- missing values;
- duplicate data;
- an obvious numeric outlier.

Verify that the resulting report is meaningful.

---

### Phase 10: Add Docker Support

Implement:

```text
Dockerfile
.dockerignore
```

Verify:

```bash
docker build -t csv-quality-reporter .
docker run --rm csv-quality-reporter
```

The default run must generate a real report.

---

### Phase 11: Complete README

Document only commands and behaviors that have been verified.

Include:

- setup;
- usage;
- tests;
- Docker;
- mounted CSV usage;
- IQR explanation;
- edge-case behavior;
- smoke-test procedure;
- limitations.

---

### Phase 12: Final Verification

Before submission:

```bash
pytest
```

Then manually complete the full smoke-test procedure.

Confirm:

- normal CSV works;
- text-only CSV works;
- header-only CSV works;
- missing file returns a clear error and nonzero code;
- completely empty file returns a clear error and nonzero code;
- Docker image builds;
- default container performs meaningful analysis;
- mounted CSV works;
- README commands match actual project behavior.

---

## 25. Final Architecture

The finalized architecture is:

```text
              main.py
                 │
                 ▼
           argparse CLI
                 │
                 ▼
             load_csv()
                 │
                 ▼
        analyze_dataframe()
                 │
          ┌──────┴──────┐
          │             │
   general checks   numeric analysis
                        │
                        ▼
             detect_iqr_outliers()
                 │
                 ▼
          structured results
                 │
                 ▼
           format_report()
                 │
                 ▼
               stdout
```

Core separation of responsibilities:

```text
input handling → analysis → presentation
```

This architecture is intentionally small, testable, and easy to explain while still meeting the project's software-engineering requirements.