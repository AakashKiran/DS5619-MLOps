# Week 11 - Model Compression Benchmark

## My Approach

### 1. Understanding the Lab

The goal of this lab is to compare model compression methods by measuring storage size, prediction accuracy, and inference latency. The benchmark uses a linear classifier with 256 weights and 300 evaluation examples generated from those weights. Forty weights carry the main signal, while the remaining 216 are small-magnitude noise.

I generated the data for my student ID using:

`python generate_for_student.py --student-id 142301002`


### 2. Implementing `compression.py`

#### 2.1 `model_size_bytes(weights, dtype_bytes)`

This function calculates dense model storage by multiplying the number of weights by the number of bytes used for each weight.

#### 2.2 `prune_weights(weights, sparsity)`

This function removes the requested fraction of weights with the smallest absolute values. I sorted the weight indices by magnitude, copied the input weights, and set the selected entries to zero. Then I returned the edited copy so original weights aren't altered.

#### 2.3 `sparse_coo_size_bytes(weights, value_bytes, index_bytes)`

This function counts the nonzero weights and computes size for both its value and its index. With FP32 values and 4-byte indices, each surviving value occupies 8 bytes. This allows the pipeline to compare pruning in dense storage with the smaller size possible when using a sparse representation.

#### 2.4 `quantize_int8(weights)`

This function sets the scale to the largest absolute weight divided by 127, rounds each scaled weight to the nearest integer, and clamps the result to the range [-127, 127]. If all weights are zero, it returns zero-valued integers and a scale of 1.0. `dequantize_int8()` converts the integers back to approximate floating-point values before the pipeline measures accuracy.

#### 2.5 `benchmark_model(label, weights, eval_examples, dtype_bytes, n_latency_reps)`

This function calculates accuracy by comparing predictions against the evaluation labels. It measures latency by timing a full pass over the examples repeatedly, then reports the average time per pass in milliseconds. The returned result also includes the model label and its dense size in bytes.

### 3. Results and Observations

At the default 70% pruning level, the baseline and both pruned variants achieved 100% accuracy. The dense pruned model remained 1,024 bytes because zero-valued weights still occupy storage. The COO version contained 77 nonzero weights and used 616 bytes (about 1.66x smaller than baseline). INT8 quantization used 256 bytes, exactly one fourth of the FP32 baseline, and also achieved 100% accuracy in this run.

For the 95% sparsity experiment, I changed `PRUNE_SPARSITY` in `src/run_pipeline.py` and reran the pipeline. The pruned models had 79.33% accuracy. Pruning first removed the 216 small noise weights, then removed 27 of the 40 informative weights, leaving 13 nonzero weights. Dense storage remained 1,024 bytes, while COO storage fell to 104 bytes (9.85x smaller than baseline). This shows that pruning can save storage when represented sparsely, but pruning away informative weights can reduce accuracy.

Latency measurements varied slightly between runs. In the 95% run, the reported per-pass latencies were 2.1153 ms for baseline FP32, 2.2784 ms for the pruned variants, and 2.1244 ms for INT8. The measured differences are small and do not imply that pruning or quantization necessarily improves runtime in this simple benchmark.

### 4. Testing and Running the Pipeline

I ran the benchmark with `python src/run_pipeline.py`

The pipeline prints the size, compression ratio, accuracy, and latency for each variant, then writes the results to `compression_report.json`.

I ran the self-checks with `pytest tests/ -q`

All 13 tests passed.
