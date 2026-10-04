# Fitness Session Analyzer

**Course:** ACIT 4420 - Python Programming Assignment (Option A)  
**Student:** Per-Erik Glærum Gronvik  
**Student Number:** pegro6469 385710

ACIT 4420 Assignment II, Option A. This version reads the supplied participant
and fitness-session CSV files, validates rows, converts numeric values, and
groups valid observations by session ID.

## Run

From the repository root, run with the supplied input files:

```bash
python3 main.py --profiles data/participants.csv --sessions data/fitness_sessions.csv --output output
```

The program validates the participant profiles and session observations, then
writes its reports to `output/`. It uses only the Python standard library. The
`--profiles`, `--sessions`, and `--output` options accept paths relative to the
repository root (absolute paths also work). The test file
`data/fitness_sessions_invalid.csv` is processed by default. Its rows are
validated but never included in session analysis. To use a different test file,
provide its path with `--invalid-sessions`:

```bash
python3 main.py --profiles data/participants.csv --sessions data/fitness_sessions.csv --invalid-sessions data/fitness_sessions_invalid.csv --output output
```

`--sessions` is also available as `--valid-sessions`; `--output` is also
available as `--output-dir`. The completion summary reports accepted rows,
rejected rows, and the report files created. Accepted rows count accepted
participants and observations added from the valid session file. Rejected CSV
rows count distinct source-file and row-number pairs with one or more recorded
issues, so multiple issues for the same row count once.

The output directory contains three files:

- `analysis_summary.csv` has one summary row for each processed session.
- `analysis_report.txt` explains the analysis result for each session.
- `rejected_records.txt` lists rejected input rows with their source, row
  number, field, and rejection reason.

## Tests

Run the CSV validation and reused domain-analysis tests from the repository root:

```bash
python3 -m unittest test_csv_validation test_domain_analysis
```

## Structure

| Path | Purpose |
| --- | --- |
| `main.py` | Parses CLI arguments and starts the application. |
| `data/` | Contains the supplied Option A CSV files and data dictionary. |
| `src/__init__.py` | Marks `src` as a regular Python package. |
| `src/application.py` | Coordinates loading, validation, analysis, and reports. |
| `src/calculations.py` | Calculates session summary values. |
| `src/classifier.py` | Classifies session results. |
| `src/csv_validation.py` | Validates CSV schemas, identifiers, and values. |
| `src/exceptions.py` | Defines the application's custom exceptions. |
| `src/observation.py` | Represents a validated fitness observation. |
| `src/participant.py` | Represents a participant and reference values. |
| `src/perdas.py` | Provides the reusable CSV reader. |
| `src/report.py` | Builds and writes analysis reports. |
| `src/session.py` | Groups observations for a participant and session. |
| `src/validation.py` | Shares measurement ranges and signal-quality rules. |

## Validation and Signal Quality

- The [data dictionary](data/DATA_DICTIONARY.txt) lists the input fields, units,
  identifier formats, and valid numeric ranges.
- Rows must have the required fields, valid identifiers, convertible numeric
  values, and measurements within those ranges.
- `signal_quality` must be between `0.0` and `1.0`. Values below `0.7` are kept
  as low-quality observations but excluded from the usable observations used
  for analysis.
- A session with fewer than `MINIMUM_USABLE_OBSERVATIONS` (currently 3) usable
  observations is marked insufficient for
  classification.