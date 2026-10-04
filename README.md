# Fitness Session Analyzer

**Course:** ACIT 4420 - Python Programming Assignment (Option A)  
**Student:** Per-Erik Glærum Gronvik  
**Student Number:** pegro6469 385710

ACIT 4420 Assignment II, Option A. This version reads the supplied participant
and fitness-session CSV files, validates rows, converts numeric values, and
groups valid observations by session ID.

## Run

From the repository root, run with the supplied default inputs:

```bash
python3 main.py
```

The program uses the supplied `data/participants.csv` profile automatically,
reads `data/fitness_sessions.csv` and `data/fitness_sessions_invalid.csv` by
default, and writes reports to `output/`. It uses only the Python standard
library. You can provide alternative session files or an output directory:

```bash
python3 main.py --sessions data/fitness_sessions.csv --invalid-sessions data/fitness_sessions_invalid.csv --output-dir output
```

`--sessions` is also available as `--valid-sessions`.

## Structure

```text
main.py                 coordinates loading, validation, grouping, and summary output
data/                   supplied Option A CSV files and data dictionary
src/csv_validation.py   CSV schema, identifier, conversion, and range checks
src/perdas.py            reusable CSV reader
src/                    participant, observation, session, and analysis modules
```

## Validation and Signal Quality

- Rows must have the required fields, valid identifiers, convertible numeric
  values, and measurements within the documented ranges.
- `signal_quality` must be between `0.0` and `1.0`. Values below `0.7` are kept
  as low-quality observations but excluded from the usable observations used
  for analysis.
- A session with fewer than `MINIMUM_USABLE_OBSERVATIONS` (currently 3) usable
  observations is marked insufficient for
  classification.