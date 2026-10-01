# Independent Tester Report

**Student:** Jacey Dai  
**NetID:** zd86  
**Project:** IDS 706 — Option 3: CSV Data Quality Reporter

## Scope

This report documents an independent review of the CSV Data Quality Reporter against the approved Architect plan, followed by the targeted corrections accepted after the audit. The application remains beginner-friendly and keeps all application code in `main.py` and `reporter.py`.

The protected files were not modified:

- `docs/transcripts/plan.md`
- `docs/transcripts/zd86_architect.txt`
- `docs/transcripts/zd86_builder.txt`

## Independent Audit Summary

The initial implementation had a sound core: specific CLI error handling, correct exit codes, stderr use for expected failures, correct IQR calculations, safe handling of text-only/header-only data, and no unnecessary architectural complexity. The original test suite passed, but several plan requirements were not covered strongly enough by tests.

The audit identified these gaps:

- missing values reported counts but not percentages;
- duplicate rows reported a count but not a percentage;
- Q1, Q3, IQR, lower bound, and upper bound were calculated but not displayed;
- report headings differed from the approved plan;
- CLI tests did not assert all required report sections;
- tests did not fully verify exact IQR statistics, zero-row percentages, or all required numeric edge cases through the CLI;
- README documentation did not fully describe the required percentages, IQR details, known limitations, or complete smoke-test procedure.

## Corrections Made

### Missing values

`missing_values()` now returns, for every column:

- missing count;
- missing percentage calculated as `count / total rows * 100`.

For a zero-row DataFrame, the percentage is `0.0`, displayed as `0.00%`.

### Duplicate rows

`duplicate_count()` now returns:

- duplicate count;
- duplicate percentage.

For a zero-row DataFrame, the percentage is `0.0`, displayed as `0.00%`.

### IQR reporting

For every usable numeric column, the report now displays:

- Q1;
- Q3;
- IQR;
- lower bound;
- upper bound;
- outlier count;
- outlier values when any exist.

Missing numeric values are removed before quartile and outlier calculations. All-missing numeric columns produce a clear message and zero outliers rather than crashing.

### Report headings

The user-facing headings now match the Architect plan:

- `Dataset Dimensions`
- `Column Data Types`
- `Missing Values`
- `Duplicate Rows`
- `Numeric Summary Statistics`
- `Numeric Outliers — IQR Method`

### Tests

The unit and CLI integration tests were strengthened to verify:

- missing counts and percentages;
- duplicate count and percentage;
- zero-row percentages;
- exact Q1, Q3, IQR, lower bound, upper bound, and outlier count;
- missing-value exclusion from IQR calculations;
- all required report headings;
- header-only dimensions and percentages;
- constant numeric data through the CLI;
- numeric data with missing values through the CLI;
- an all-missing numeric column through the CLI;
- invalid-input errors on stderr with empty stdout and no traceback.

### README

The README now documents:

- missing and duplicate percentages;
- displayed IQR statistics;
- current edge-case behavior;
- known limitations;
- `--help` as part of smoke testing;
- zero-byte CSV testing;
- full pytest execution;
- Docker build, default run, and mounted-file run commands.

## Final Automated Test Evidence

Command:

```bash
python -m pytest -v
```

Final result:

```text
collected 18 items

tests/test_cli.py::test_successful_cli_returns_zero_and_all_sections PASSED
tests/test_cli.py::test_missing_file_returns_nonzero_stderr_only_without_traceback PASSED
tests/test_cli.py::test_directory_returns_nonzero_stderr_only_without_traceback PASSED
tests/test_cli.py::test_zero_byte_csv_returns_nonzero_stderr_only_without_traceback PASSED
tests/test_cli.py::test_header_only_csv_returns_zero_with_dimensions_and_percentages PASSED
tests/test_cli.py::test_text_only_csv_returns_zero_and_skips_numeric_sections PASSED
tests/test_cli.py::test_constant_numeric_csv_works_through_cli PASSED
tests/test_cli.py::test_numeric_with_missing_values_works_through_cli PASSED
tests/test_cli.py::test_all_missing_numeric_csv_works_through_cli PASSED
tests/test_reporter.py::test_basic_shape_missing_and_duplicates PASSED
tests/test_reporter.py::test_zero_row_percentages_are_zero PASSED
tests/test_reporter.py::test_numeric_summary_returns_testable_structure PASSED
tests/test_reporter.py::test_iqr_detects_outlier_with_exact_statistics PASSED
tests/test_reporter.py::test_constant_numeric_column_has_zero_outliers PASSED
tests/test_reporter.py::test_missing_numeric_values_are_excluded_from_iqr_calculation PASSED
tests/test_reporter.py::test_all_missing_numeric_column_does_not_crash PASSED
tests/test_reporter.py::test_text_only_skips_numeric_analysis_clearly PASSED
tests/test_reporter.py::test_header_only_dataframe_generates_report_with_zero_percentages PASSED

18 passed
```

Test environment used for this verification:

- Python 3.13.5
- pytest 9.0.2
- Linux execution environment

## CLI Smoke-Test Evidence

The following cases were executed independently after the changes:

| Case | Exit code | stdout | stderr | Traceback |
|---|---:|---|---|---|
| `--help` | 0 | present | empty | no |
| `data/sample.csv` | 0 | report | empty | no |
| missing file | 1 | empty | error message | no |
| directory path | 1 | empty | error message | no |
| zero-byte CSV | 1 | empty | error message | no |
| header-only CSV | 0 | report | empty | no |
| text-only CSV | 0 | report | empty | no |
| constant numeric CSV | 0 | report | empty | no |
| numeric data with missing values | 0 | report | empty | no |
| all-missing numeric column | 0 | report | empty | no |

For the numeric-with-missing smoke case containing `1, 2, missing, 3, 4, 100`, the report showed:

```text
Q1: 2
Q3: 4
IQR: 2
Lower bound: -1
Upper bound: 7
Outlier count: 1
Outlier values: [100.0]
```

This confirms that the missing value was excluded from the quartile/outlier calculation and that the IQR result is correct.

For the all-missing numeric column, the report included:

```text
No non-missing values available for IQR calculation.
Outlier count: 0
```

## Docker Status

Docker runtime verification was **not performed** because Docker is unavailable in the tester execution environment (`docker` was not present on the executable path).

The Dockerfile and README commands were inspected for consistency. The project uses:

```dockerfile
ENTRYPOINT ["python", "main.py"]
CMD ["data/sample.csv"]
```

The documented default and mounted-file commands are consistent with that configuration. Docker build/run success is intentionally not claimed here and should be verified independently on a machine with Docker installed.

## Remaining Limitations

The project intentionally remains small and beginner-friendly. Current limitations are:

- CSV input only;
- pandas dtype inference determines which columns are considered numeric;
- mixed numeric/text columns can be treated as text and skipped by numeric analysis;
- custom missing-value strings such as `unknown` are not automatically treated as missing unless pandas recognizes them;
- IQR outliers are statistical flags and do not prove a record is erroneous;
- CSV files are loaded fully into memory, so the project is not optimized for very large datasets.

## Final Assessment

After the targeted corrections, the implementation now satisfies the audited reporting requirements and the strengthened automated/CLI checks pass. No redesign, classes, frameworks, databases, configuration systems, or web interfaces were introduced.
