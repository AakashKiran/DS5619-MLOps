# NOTES.md — Week 3: ETL and Data Validation

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
142301002
Seed Generated : 1634648564

## Quarantine count vs. the 7 known injected problems

<!-- How many rows ended up quarantined, and does that match the 7 known
     injected problems? (It won't match exactly — some rows may trip more
     than one expectation. Explain the discrepancy if there is one.) -->

* 6 rows ended up being quarantined
* A total of 8 violations were found (2 rows - 21 and 577 had 2 violations each)
This doesn't exactly match the 7 known injected problems because rows 21 and 577 have tripped 2 expectations each

### Summary of Expectations

| Expectation              | Column              | No: of Violations | Row Indices         |
| ------------------------ | ------------------- | ----------------- | ------------------- |
| `expect_column_not_null` | `amount`            | 2                 | 21, 577             |
| `expect_column_not_null` | `card_id`           | 1                 | 554                 |
| `expect_column_positive` | `amount`            | 3                 | 21, 438, 577        |
| `expect_column_in_set`   | `merchant_category` | 1                 | 507                 |
| `expect_column_unique`   | `transaction_id`    | 1                 | 350                 |