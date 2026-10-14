# Week 10 - Fairness and Robustness Audit

## My Approach

### 1. Understanding the Lab

The objective of this lab to measure the recall of the vehicle detector for each vehicle class, identify classes with lower recall, and check how the results change when adversarial perturbations are applied to the input images.

The lab uses a mock detector that identifies reddish pixel regions using fixed colour thresholds. The generated fixtures contain 60 images across two camera profiles: daylight and low-light. Smaller vehicle classes, particularly Bicycle and Two-wheeler, have smaller bounding boxes and are therefore harder to detect.

### 2. Implementing `fairness_audit.py`

I implemented the four functions in `fairness_audit.py`.

#### 2.1 `compute_iou(box_a, box_b)`

This function calculates the Intersection over Union (IoU) between two bounding boxes represented as `[x, y, width, height]`.

I converted the boxes into corner coordinates, calculated the width and height of their intersection, and used these values to calculate the intersection area. The intersection width and height are found by subtracting the maximum of the two boxes’ left (or top) coordinates from the minimum of their right (or bottom) coordinates, clamping each result to zero to handle non-overlapping boxes. I then calculated the union area and returned the ratio of intersection area to union area. The function returns `0.0` when the union area is zero.


#### 2.2 `match_ground_truth(gt_boxes, detections, iou_threshold)`

This function checks whether each ground-truth bounding box matches at least one detection.

For every ground-truth box, I calculated its IoU with the detected boxes. If any detection had an IoU greater than or equal to the specified threshold, the ground-truth box was marked as detected. The function returns a list of Boolean values indicating which ground-truth boxes were successfully matched.

#### 2.3 `audit_by_category(coco_path, fixtures_dir, iou_threshold, transform)`

This function performs the recall audit for each vehicle class.

I loaded the COCO-style annotation file and created mappings between category IDs and names, as well as between image IDs and their annotations. I then loaded each image, converted it to RGB, applied the optional image transformation, and passed it to the mock detector.

The detected boxes were matched against the ground-truth boxes using `match_ground_truth()`. For each class, I maintained the total number of ground-truth boxes and the number successfully detected. Recall was calculated as:

`Recall = Detected ground-truth boxes / Total ground-truth boxes`

Classes with no ground-truth boxes were excluded from the returned results. The detector's predicted class labels were not used to determine the ground-truth class of a matched object.

#### 2.4 `find_underperforming_categories(category_stats, recall_threshold)`

This function identifies classes whose recall falls below the specified threshold.

I iterated through the per-class recall results, selected classes with recall strictly below the threshold, and sorted them from lowest recall to highest recall. This allows the classes with the poorest detection performance to be examined first.

### 3. Implementing `adversarial.py`

Next, I implemented the three functions in `adversarial.py` to evaluate the detector under adversarial perturbations.

#### 3.1 `perturb_image(img, eps)`

This function creates a new image by changing the RGB channels of every pixel. The red channel is decreased by `eps`, while the green and blue channels are increased by `eps`.

I used `Image.split()` to separate the channels, `Image.point()` to apply the changes to individual channel values, and `Image.merge()` to combine them into a new RGB image. Each value is clamped to the range `[0, 255]`, and the original image is not modified.


#### 3.2 `audit_under_attack(coco_path, fixtures_dir, eps_values, iou_threshold)`

This function repeats the category-based audit for each specified perturbation budget.

I used the `transform` argument of `audit_by_category()` and passed a lambda function that applies `perturb_image()` with the current value of `eps`. The results are stored in a dictionary mapping each perturbation budget to its per-class recall statistics.

The pipeline evaluates `eps` values of `0`, `10`, `20`, `30`, and `40`. The value `eps=0` provides the clean baseline for comparison.

#### 3.3 `find_most_fragile(attack_stats, eps, top_k)`

This function identifies the classes that experience the largest recall drops under attack.

For each class, I subtracted the recall at the selected perturbation budget from its clean recall. I rounded the resulting drop to four decimal places and sorted the classes by decreasing recall drop. Alphabetical order is used to break ties. Finally, the function returns the first `top_k` classes.

The pipeline uses `eps=20` for this ranking. This measures how much performance each class loses compared with its clean baseline, rather than simply identifying the classes with the lowest recall after the attack.

### 4. Testing and Running the Pipeline

After completing the seven functions, I ran the pipeline using:

`python src/run_pipeline.py`

This performs the clean audit, evaluates the detector under the different perturbation budgets, and generates `fairness_report.json`.

I then ran the self-checks using:

`pytest tests/ -q`

All test cases passed.
