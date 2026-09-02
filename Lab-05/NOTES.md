# NOTES.md — Week 5: Model Registry Governance

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student_id: 142301002
- seed: 494068276

## Which candidate reached Production, and why?

<!-- Which candidate ended up in Production, and why? -->
Candidate B reached Production because its F1 score was 0.854, which is above the registry's 0.70 production threshold, and it had a completed model card. Candidate A was blocked because its F1 score was 0.466, below the threshold.

## Gating stale feature data

<!-- What would you need to add to promote_model's gate if you also wanted
     to block promotion of a model trained on stale (e.g. >30-day-old)
     feature data? -->

I would record the feature data's `as_of` timestamp or a relevant time specific variable in the model manifest. Then a comparison of that timestamp with the current UTC time in `promote_model` will be done. `GovernanceError` will be raised when the data is more than 30 days old, before allowing promotion.


## Scaling the gate to 40 candidates

<!-- Tying back to this week's AutoML/HPO framing: if a hyperparameter
     search had handed you 40 candidates instead of 2, what in your
     register_model/promote_model design would need to change (or
     genuinely wouldn't) to gate 40 instead of 2? -->

The registry functions would not need to change as `register_model` already creates a separate immutable version for every candidate, and `promote_model` evaluates the model card and metrics for whichever version is passed to it. 

However, the pipeline (run_pipeline.py) would need to loop over all 40 candidates rather than the current hardcoding for just candidates a and b before deciding the best model and promoting it. 

## My approach

In `register_model`, I generate the next version number by scanning the model's existing version folders. Each  candidate is stored in its own directory with the copied `model.json` and a `manifest.json` containing its name, metrics, creation time, and initial stage. This prevents a new candidate from overwriting an older one and preserves model history.

For `generate_model_card`, I first validate every required fields. The function rejects missing, empty, whitespace-only, or `TODO` in values. After validation, it reads the metrics from the model's manifest and writes a `model_card.json` containing the model identity, governance fields, metrics, and creation time. This keeps the governance information attached to the specific model version.

In `promote_model`, I implemented Production as a governance gate. A model can reach Production only when it has a model card and its F1 score meets the 0.70 threshold. Staging does not require these Production checks. Before promoting a new version to Production, the function archives any previous Production version. It then updates the selected manifest and appends a history entry recording the old stage, new stage, and time of promotion.

Finally, `get_production_model` scans the registered versions and returns the manifest whose stage is `Production`. If no version is in Production, it returns `None`. This provides a simple source of truth for which model is currently deployed instead of relying on memory or an external note.
