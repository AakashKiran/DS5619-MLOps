# NOTES.md — Week 11: Model Compression Benchmark

**Student ID used with `generate_for_student.py`:**
- student_id: 142301002
- seed: 213273277


## pruned_dense_fp32 vs. pruned_sparse_coo

<!-- Compare pruned_dense_fp32 and pruned_sparse_coo in your report — same
     weights, same accuracy, very different size_bytes. Explain why in your
     own words (tie it to the lecture's pruning pitfall). -->

Both variants use the same weights after 70% pruning and have 100% accuracy. However, `pruned_dense_fp32` still stores all 256 weights as FP32, so it remains 1,024 bytes, the same size as the baseline. Pruning sets weights to zero, but dense storage still reserves space for those zeros.

`pruned_sparse_coo` stores only the 77 non-zero weights, along with each weight's index. At 4 bytes for the value plus 4 bytes for the index, its size is 77 * 8 = 616 bytes (about 1.66x smaller than the baseline). This illustrates the pruning pitfall: pruning alone does not reduce model storage unless the model is stored in a sparse-aware format.


## The 0.95-sparsity experiment

<!-- Try editing PRUNE_SPARSITY in src/run_pipeline.py to 0.95 and re-run —
     what happens to accuracy, and why does that make sense given only 40
     of the 256 weights are actually informative? -->

At 95% sparsity, accuracy for the pruned variants falls to 79.33%, while the baseline and INT8 versions remain at 100%. The pruning procedure removes the 216 near-zero noise weights first. To reach 243 zeroed weights out of 256, it must also discard 27 informative weights, leaving just 13 to contribute to the predictions. With much of the useful signal gone, the classifier makes more incorrect predictions.

Storage also depends on how the pruned weights are represented. The dense model remains 1,024 bytes because even zero-valued weights require the same amount of storage as any other value of weight. COO storage records only the 13 nonzero values and their indices, using 104 bytes. This demonstrates the tradeoff: aggressive pruning can greatly reduce sparse storage, but removing useful weights can hurt predictive accuracy.
