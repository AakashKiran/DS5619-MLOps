# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student_id: 142301002
- seed: 1840943052


## Drift level vs. expectation

<!-- What drift level did the report show, and does that match what you'd
     expect given the two cameras were built with deliberately different
     visual statistics? -->


## What confidence-score-only monitoring misses

<!-- What would you monitor IN ADDITION to confidence score if you had
     access to ground-truth labels a day later? (Tie this to the kinds of
     drift from the lecture — which one does confidence-score-only
     monitoring miss?) -->

## My Approach

Initially I completed the instructions mentioned in the setup section of `README.md`. This involved creating the virtual environment, installing the required dependencies inside it and generating the custom fixture data using my student ID. The generated fixture data provides two synthetic camera conditions: `camera_A_daylight`, which is treated as the reference distribution, and `camera_B_lowlight`, which is treated as the live distribution being monitored.

I then implemented the `extract_confidence_scores()` function in `src/drift_monitor.py`. The purpose of this function is to obtain the confidence-score distribution produced by the detector for a given camera directory. I first used `glob.glob()` to obtain all `.jpg` images in the specified directory and sorted the resulting list to ensure deterministic processing. For each image, I loaded it using `Image.open(path).convert("RGB")` and passed it to the provided `mock_detector` using `det.detect(image)`. Since the detector can produce multiple detections for a single image, I iterated through all the detections and extracted the `score` value from each detection. These scores were appended to a single list, resulting in a flat list containing the confidence scores from all detections across all images in the camera directory.

I then implemented the `compute_psi()` function to compare the confidence-score distributions of the reference and live cameras using the Population Stability Index (PSI). I divided the `[0, 1]` confidence-score range into equal-width bins and stored the lower boundary of each bin. Each score was assigned to the appropriate bin by finding the first lower boundary greater than the score and assigning the score to the preceding bin. Since a score of exactly `1.0` does not satisfy this condition for any bin, it was explicitly assigned to the final bin. After obtaining the bin counts for both the reference and live distributions, I converted the counts into proportions by dividing each count by the total number of scores in the corresponding distribution. To avoid division by zero and `log(0)` during the PSI calculation, each proportion was clamped to a minimum value of `1e-4`. Finally, I calculated the PSI by summing the contribution from each bin using the specified PSI formula.

