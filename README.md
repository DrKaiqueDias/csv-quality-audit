# CSV Quality Audit

[![Python checks](https://github.com/DrKaiqueDias/csv-quality-audit/actions/workflows/tests.yml/badge.svg)](https://github.com/DrKaiqueDias/csv-quality-audit/actions)

A Python tool for checking a CSV before using it elsewhere. It flags missing required values, invalid numbers and rows with the wrong number of fields.

The focus is straightforward: find structural problems and return a report that is easy to act on. The file is read row by row, so it does not need to fit in memory.

## Try it

```sh
python audit.py examples/sample.csv --required id amount --numeric amount
```

The synthetic example contains **4 records and 2 failing records**. It deliberately exits with status **1**. The JSON report lists counts by column without printing raw cell contents.

```sh
python audit.py examples/sample.csv
```

Without explicit constraints, the tool reports missing values and fails only on malformed record widths. It does not infer business rules.

## Rules

- Header names must be unique and non-empty; rule names must match exactly.
- Whitespace-only values are missing. A blank numeric value is permitted unless also required.
- Numeric values must be parseable finite floats; NaN and infinity fail.
- Quoted commas and quoted multiline values are supported.
- Physically blank lines are ignored. Records with a wrong field count are counted as malformed; their column values are not audited.
- A row with several failures counts once in `failed_rows`.

Exit codes: **0** passed; **1** quality failures; **2** configuration, parse or file error. Header-only input is an error. Runtime is O(rows × columns), with O(columns) auxiliary memory; no full dataset is stored.

## Limits

This is a structural audit, not deduplication, schema inference or anonymization. Reports include column names, so review schemas before sharing a report. The CLI never modifies its input.

## Development

Requires **Python 3.11+**. Uses only the standard library; no installation or API keys.

```sh
python -m unittest discover -v
```

Tests run on Python 3.11, 3.12 and 3.13 through GitHub Actions. The sample data is synthetic.

## Design choices

The audit keeps counts instead of storing rows. Reports show which columns need attention without copying their cell contents. Input files are left unchanged.

## License

MIT. Maintained by [Kaique Dias](https://github.com/DrKaiqueDias).

