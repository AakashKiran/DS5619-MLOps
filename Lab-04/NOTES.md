# NOTES.md — Week 4: Versioning, Feature Store & Lineage

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- 142301002
- Seed Generated: 4267196089

## v1 vs. v2 manifest comparison

The v1 and v2 feature-group manifests differ in the following respects
- v1 has 500 rows, v2 has 125
- v1 has amount, v2 has amount_minor_units
- v1 has country, v2 has country_code
- The content_hash generated are different
- v2 has an additional parameter - "device_fingerprint"


## Why treat amount_minor_units differently from amount?

`amount_minor_units` is 100 times smaller than `amount` due to difference in their units. This is why `build_features` divides the v2 value by 100 before calculating averages and maxima. Otherwise v2 amounts would be 100 times too large and the aggregates would not be comparable with v1. 

