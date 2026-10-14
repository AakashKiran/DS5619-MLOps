# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student_id: 142301002
- seed: 1812353673

## Which classes got flagged?

<!-- Which classes got flagged, and does that match what you'd expect given
     how generate_for_student.py built the fixtures? -->

The audit flagged four classes below the 90% recall threshold: Bicycle (69.57%), MUV (81.82%), SUV (86.67%), and Two-wheeler (88.89%).

This mostly matches what the fixture generator was designed to do. Bicycle and Two-wheeler are harder to detect because their bounding boxes are smaller. The generator makes sure both classes have recall below 90%, while the large vehicle classes stay above this limit. MUV and SUV were also flagged in my run. Since there are only a few examples of each class, their low recall might be due to the small number of examples rather than a consistent problem. This shows why we should check recall for each class instead of looking only at the overall performance.

## If the grouping variable were a protected attribute

<!-- Tying back to the framing note: what would change about this audit's
     stakes and your obligations as an engineer if the grouping variable
     were a protected demographic attribute instead of a vehicle class? -->

If the grouping variable were a protected demographic attribute instead of a vehicle class, the audit would have to consider the ethical and legal stakes which are far more important. A disparity could mean that the system performs worse for a particular demographic group, potentially leading to unequal treatment or harm. As an engineer, I would need to investigate the cause, validate the results across sufficiently representative data, document limitations, and work toward reducing the disparity before deployment. I would also need to consider privacy, applicable regulations, and continuous monitoring. A passing overall recall would not be enough if a protected group experienced substantially worse performance.

## Which attack could corrupt this audit?

<!-- Name one lifecycle stage and attack from the lecture (data poisoning,
     model theft, or adversarial examples) that could silently corrupt THIS
     audit's result, and one control from the lecture that would reduce the
     risk. -->

Data poisoning during the data collection or labelling stage could silently corrupt this audit. For example, an attacker could modify ground-truth bounding boxes or category labels so that the measured recall becomes artificially high or low for particular classes. The audit might then report a misleading disparity even if the detector itself had not changed. A useful control would be dataset versioning, combined with validation checks for annotation consistency and review of suspicious changes before the data is used.

## Would SHAP or LIME explain a missed detection?

<!-- Pick one missed ground-truth box in a flagged class. An auditor asks
     you to explain WHY the detector missed it, not just that it did. Would
     SHAP or LIME actually help you answer that for a bounding-box detector
     — and if not, what's different about this detector's inputs/outputs
     that breaks the assumption both tools make? -->

SHAP or LIME would not automatically provide a reliable explanation for a missed detection in this bounding-box detector. Both methods are commonly used to explain a model's prediction by relating input features to a defined output, but an object detector produces a variable set of bounding boxes, categories, and confidence scores rather than one simple prediction. When an object is missed, there may be no corresponding detection score to explain directly.

For this mock detector, I would first inspect the missed ground-truth box and its pixel values. The detector only accepts pixels satisfying the rule r > 120, r − g > 40, and r − b > 40, and it ignores connected reddish regions containing fewer than 20 pixels. A small object or a region whose colours fail these conditions could therefore be missed. SHAP or LIME could potentially be adapted to explain a carefully defined detection-related output, but they would not automatically identify the reason for a missing bounding box. Here, examining the explicit rule and the missed region is more direct.


## What did your attack show?

<!-- Using fairness_report.json["adversarial"]: at what eps does each flagged
     class fall further? Which class is most fragile, and is it the same
     class the clean audit flagged? Compare the drop ranking
     (most_fragile) with lowest_recall_under_attack — do they agree, and
     which is the better measure of who is hurt? What does that say about who bears the
     cost of an attack (or of an unmonitored failure)? Then: what would
     adversarial training or input validation look like for this detector,
     and why does a rule this simple break so much more easily than a CNN
     (or does it)? -->

The attack progressively reduced recall for the classes flagged by the clean audit, although the effect differed by class.

- Bicycle: Recall fell from 0.6957 at eps=0 to 0.4783 at eps=10, 0.3043 at eps=20, and 0.0435 at eps=30. It remained at 0.0435 at eps=40.
- MUV: Recall fell from 0.8182 to 0.7273 at eps=10, remained at 0.7273 at eps=20, and then fell to 0.4545 at eps=30 and 0.2727 at eps=40.
- SUV: Recall fell from 0.8667 to 0.8 at eps=10, remained at 0.8 at eps=20, and then fell to 0.7333 at eps=30 and 0.5333 at eps=40.
- Two-wheeler: Recall remained at 0.8889 for eps=0 and eps=10, then fell to 0.7778 at eps=20, 0.5556 at eps=30, and 0.4444 at eps=40.

At eps=20, the three largest recall drops (most_fragile) were Bicycle (0.3914), Three-wheeler (0.28), and Tempo-traveller (0.2143). The three classes with the lowest absolute recall under attack were Bicycle (0.3043), Three-wheeler (0.64), and MUV (0.7273).

The rankings agree on Bicycle and Three-wheeler, but differ on the third class. The recall-drop ranking measures how much damage the attack caused relative to the clean baseline, whereas absolute recall shows which classes perform worst after the attack. Neither measure is sufficient by itself: a class can already have poor recall before an attack, while another can experience a large decline due to the attack. Together, they show both the pre-existing performance disparity and the additional damage caused by the perturbation.

The attack lowers red values and raises green and blue values, pushing pixels away from the detector's fixed colour rule. Adversarial training for a real detector could include perturbed images during training so that the model learns to handle such changes. Input validation could monitor unusual colour distributions or shifts from the expected input characteristics and flag suspicious inputs for further inspection. However, input validation alone would not guarantee detection of every adversarial example.

This mock detector is especially brittle because its decision depends on explicit colour thresholds and connected-pixel rules. Small changes can push pixels across those thresholds and cause entire regions to disappear from its detections. A trained CNN can learn richer visual features than this fixed rule, but that does not guarantee robustness as real detectors also require robustness testing and suitable mitigations.
