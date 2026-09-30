# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student_id: 142301002
- seed: 1840943052

## Drift level vs. expectation

<!-- What drift level did the report show, and does that match what you'd
     expect given the two cameras were built with deliberately different
     visual statistics? -->

The generated `drift_report.json` reported a PSI value of **0.1042**, which corresponds to a **moderate** drift level. This is consistent with the expected behavior because `camera_A_daylight` and `camera_B_lowlight` were deliberately generated with different visual statistics. The reference camera produced 90 confidence scores with a mean of 0.9756 and a standard deviation of 0.0248, while the live camera produced 87 confidence scores, all with a confidence score of 0.98. The difference between these confidence-score distributions therefore resulted in a non-zero PSI and moderate drift classification.

## What confidence-score-only monitoring misses

<!-- What would you monitor IN ADDITION to confidence score if you had
     access to ground-truth labels a day later? (Tie this to the kinds of
     drift from the lecture — which one does confidence-score-only
     monitoring miss?) -->

If ground-truth labels were available a day later, I would additionally monitor the detector's actual prediction performance by comparing its predictions with the ground-truth labels, using appropriate evaluation metrics. Confidence-score-only monitoring can detect changes in the distribution of model confidence scores, but it cannot directly determine whether the predictions are correct. Therefore, it can miss degradation in the model's actual prediction performance even when the confidence-score distribution does not show significant drift.

## My Approach

Initially I completed the instructions mentioned in the setup section of `README.md`. This involved creating the virtual environment, installing the required dependencies inside it and generating the custom fixture data using my student ID. The generated fixture data provides two synthetic camera conditions: `camera_A_daylight`, which is treated as the reference distribution, and `camera_B_lowlight`, which is treated as the live distribution being monitored.

I then implemented the `extract_confidence_scores()` function in `src/drift_monitor.py`. The purpose of this function is to obtain the confidence-score distribution produced by the detector for a given camera directory. I first used `glob.glob()` to obtain all `.jpg` images in the specified directory and sorted the resulting list to ensure deterministic processing. For each image, I loaded it using `Image.open(path).convert("RGB")` and passed it to the provided `mock_detector` using `det.detect(image)`. Since the detector can produce multiple detections for a single image, I iterated through all the detections and extracted the `score` value from each detection. These scores were appended to a single list, resulting in a flat list containing the confidence scores from all detections across all images in the camera directory.

I then implemented the `compute_psi()` function to compare the confidence-score distributions of the reference and live cameras using the Population Stability Index (PSI). I divided the `[0, 1]` confidence-score range into equal-width bins and stored the lower boundary of each bin. For each score, I searched for the first lower boundary greater than the score and assigned the score to the preceding bin. A score of exactly `1.0` was explicitly assigned to the final bin. During testing, I also identified that scores between `0.9` and `1.0`, such as the live-camera score of `0.98`, would not satisfy any of the lower-boundary comparisons, so I added handling for this final interval and assigned such scores to the last bin. After obtaining the bin counts for both the reference and live distributions, I calculated the total number of scores in each distribution and converted the bin counts into proportions. To avoid division by zero and `log(0)` for empty bins, each proportion was clamped to a minimum value of `1e-4`. Finally, I calculated the PSI by summing the contribution from each bin using the specified PSI formula.

I then implemented the `classify_drift()` function using the PSI thresholds provided in the lab. A PSI value below `0.10` is classified as `none`, a value from `0.10` up to but not including `0.25` is classified as `moderate`, and a value of `0.25` or above is classified as `significant`.

Next, I implemented the `summarize_scores()` function to generate summary statistics for the confidence scores. The function calculates the count, mean, standard deviation, minimum and maximum values. For a single score, the standard deviation is set to `0.0` to avoid an exception from the sample standard deviation calculation. The resulting numerical values are rounded to four decimal places as required by the report format.

After completing the four functions, I ran `python src/run_pipeline.py` to execute the complete monitoring pipeline. The pipeline generated the following results:

* Reference (`camera_A_daylight`): 90 scores, mean `0.9756`, standard deviation `0.0248`, minimum `0.789`, maximum `0.98`.
* Live (`camera_B_lowlight`): 87 scores, mean `0.98`, standard deviation `0.0`, minimum `0.98`, maximum `0.98`.
* PSI: `0.1042`.
* Drift level: `moderate`.

The pipeline successfully generated `drift_report.json` containing these results.

Finally, I ran the provided test suite using `pytest tests/ -q`. All **9 tests passed**, confirming the extraction, PSI calculation, drift classification, score summarization and complete pipeline behavior.
