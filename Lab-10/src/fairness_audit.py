"""
Class-based performance disparity audit for the vehicle detector — this
week's lecture content ("Per-Group Fairness Metrics Must Be Monitored
Continuously") applied concretely.

A NOTE ON FRAMING: real fairness audits (Fairlearn, demographic parity,
equalized odds) measure disparity across PROTECTED DEMOGRAPHIC GROUPS.
BMD-45 is a vehicle-detection dataset with no demographic attributes, so
this lab applies the same underlying methodology — measure a quality metric
independently per group, then flag groups that fall below the rest — to
vehicle CLASSES instead. The statistics and the code are identical to a
real fairness audit; only the grouping variable differs. Don't walk away
thinking "vehicle class" and "protected group" are the same thing — the
audit technique generalizes, the ethical stakes of what you're auditing do
not.

The metric here is per-class RECALL: of all the ground-truth vehicles of a
given class, what fraction did the detector find at all (regardless of
what class label it guessed)? Small-vehicle classes (bicycles,
two-wheelers) are the ones a real detector — and this mock one — tend to
miss more; that's the disparity this audit should surface.

In the lecture's terms, per-class recall is the equal-opportunity check
(true-positive rate per group), not demographic parity (selection rate per
group). Each class has only ~5-30 ground-truth boxes, so a small recall gap
can be sampling noise; other mid-sized classes may also fall below the
threshold for some student IDs.

Fill in the four functions marked # TODO. (adversarial.py adds three more
for the robustness half of this lab.)
"""
import glob
import json
import os
import sys
from collections import defaultdict

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mock_detector as det


# ---------------------------------------------------------------------------
# Part 1 — Intersection over Union between two [x, y, w, h] boxes
# ---------------------------------------------------------------------------

def compute_iou(box_a, box_b):
    """box_a and box_b are [x, y, w, h]. Return the Intersection-over-Union
    (a float in [0.0, 1.0]) between them.

    Steps:
      1. Convert each box to (x1, y1, x2, y2) corners.
      2. Compute the intersection rectangle's width/height (clamp to >= 0 —
         non-overlapping boxes have zero intersection, not negative).
      3. intersection_area = inter_w * inter_h
      4. union_area = area(box_a) + area(box_b) - intersection_area
      5. Return intersection_area / union_area, or 0.0 if union_area is 0.
    """
    # TODO: implement
    box_a_corners = [box_a[0], box_a[1], box_a[0]+box_a[2], box_a[1]+box_a[3]]
    box_b_corners = [box_b[0], box_b[1], box_b[0]+box_b[2], box_b[1]+box_b[3]]
    
    overlap_width = max(0, min(box_b_corners[2], box_a_corners[2]) - max(box_b_corners[0], box_a_corners[0]))
    overlap_height = max(0, min(box_b_corners[3], box_a_corners[3]) - max(box_b_corners[1], box_a_corners[1]))
    
    intersection_area = overlap_width * overlap_height
    
    def area(b1):
        return b1[2] * b1[3]        
    
    union_area = area(box_a) + area(box_b) - intersection_area
    
    if union_area != 0:
        return intersection_area / union_area
    return 0.0
    
# ---------------------------------------------------------------------------
# Part 2 — Was each ground-truth box found by ANY detection?
# ---------------------------------------------------------------------------

def match_ground_truth(gt_boxes, detections, iou_threshold=0.3):
    """`gt_boxes` is a list of [x, y, w, h]. `detections` is a list of
    mock_detector.Detection objects (each has a .bbox attribute, also
    [x, y, w, h]).

    Return a list of booleans, same length and order as gt_boxes: True if
    that ground-truth box has IoU >= iou_threshold with AT LEAST ONE
    detection (use compute_iou), False otherwise.

    Note: this is a recall check, not one-to-one matching — the same
    detection CAN count as a match for more than one ground-truth box if it
    happens to overlap both (rare with real data, fine for this audit).
    """
    gt_iou = []
    for box in gt_boxes:
        gt_iou_flag = False
        for det in detections:
            if compute_iou(box, det.bbox) >= iou_threshold:
                gt_iou_flag = True
                break
        gt_iou.append(gt_iou_flag)
    return gt_iou
    
# ---------------------------------------------------------------------------
# Part 3 — Run the audit across every image and every class
# ---------------------------------------------------------------------------

def audit_by_category(coco_path, fixtures_dir, iou_threshold=0.3, transform=None):
    """Load the COCO annotation file at `coco_path` (has "images",
    "annotations", "categories" keys — see data/fixtures/_annotations.coco.json
    for the exact shape). For every image, run the detector once, then use
    match_ground_truth to check every ground-truth box in that image.

    Accumulate, per category NAME (not id — look up the name from
    "categories"): total ground-truth boxes seen, and how many were
    detected. Return a dict:

      {category_name: {"total": int, "detected": int, "recall": float}}

    "recall" = detected / total, rounded to 4 decimal places. Skip (don't
    include in the result) any category with zero ground-truth boxes in
    this dataset — division by zero isn't meaningful there.

    `transform` is an optional function PIL Image -> PIL Image. If it is not
    None, apply it to each image (converted to RGB) right before running
    the detector — Part 6 (adversarial.py) uses this to audit perturbed
    images. Ground-truth boxes are never transformed.

    Hint: build a lookup from image_id -> list of its annotations, and a
    lookup from category_id -> category name, before the main loop. Image
    file paths are `os.path.join(fixtures_dir, image["file_name"])`.
    """
    # TODO: implement
    with open (coco_path) as annotation_file:
        annotations = json.load(annotation_file)
        
    category_id_name_map = {}
    for cat in annotations["categories"]:
        category_id_name_map[cat["id"]] = cat["name"]
        
    image_annotations_map = {}
    for ann in annotations["annotations"]:
        if ann["image_id"] not in image_annotations_map:
            image_annotations_map[ann["image_id"]] = []
        image_annotations_map[ann["image_id"]].append(ann)
        
    category_wise_info = {}
    for i,j in category_id_name_map.items():
        category_wise_info[j] = {"total": 0, "detected": 0, "recall": 0.0}
    
    for image in annotations["images"]:
        img_path = os.path.join(fixtures_dir, image["file_name"])

        with Image.open(img_path) as image_file:
            img = image_file.convert("RGB")

        if transform is not None:
            img = transform(img)

        detections = det.detect(img)

        image_anns = image_annotations_map.get(image["id"], [])
        gt_boxes = [ann["bbox"] for ann in image_anns]

        matches = match_ground_truth(gt_boxes, detections, iou_threshold)

        for i in range(len(image_anns)):
            ann = image_anns[i]
            matched = matches[i]

            category_name = category_id_name_map[ann["category_id"]]

            category_wise_info[category_name]["total"] += 1

            if matched:
                category_wise_info[category_name]["detected"] += 1

    result = {}
    for cat in category_wise_info:
        if category_wise_info[cat]["total"] > 0:
            result[cat] = {"total": category_wise_info[cat]["total"], "detected": category_wise_info[cat]["detected"], "recall": round(category_wise_info[cat]["detected"] / category_wise_info[cat]["total"], 4)}   
    return result
            
# ---------------------------------------------------------------------------
# Part 4 — Surface the categories that fall below the bar
# ---------------------------------------------------------------------------

def find_underperforming_categories(category_stats, recall_threshold=0.90):
    """`category_stats` is the dict returned by audit_by_category.

    Return a list of (category_name, recall) tuples for every category
    whose recall is BELOW recall_threshold, sorted worst-first (lowest
    recall first).
    """
    # TODO: implement
    cat_recall = []
    for cat, info in category_stats.items():
        if info["recall"] < recall_threshold:
            cat_recall.append((cat, info["recall"]))
    cat_recall.sort(key=lambda item: item[1])
    return cat_recall
