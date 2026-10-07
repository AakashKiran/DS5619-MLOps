# NOTES.md — Week 9: Orchestrated Batch Scoring

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student_id: 142301002
- seed: 1529325810


## Notify retry count

<!-- How many attempts did notify take in your run? (Check
     dag_run_summary.json.) -->
- `Notify` took 3 attempts to run
- Below is the corresponding part of `dag_run_summary.json`

`"notify": {
      "status": "success",
      "attempts": 3
    }`


## Branch independence

<!-- Why does load still succeed even though notify — its "sibling" in the
     DAG — failed on its first two attempts? What does that tell you about
     how failures in one branch of a DAG should (or shouldn't) affect an
     unrelated branch? -->

The `load` and `notify` tasks are two separate branches of the DAG. Both of them depend on `score`, but neither of them depends on the other.

The DAG can therefore be viewed as:

```text
extract
   |
 score
 /   \
load  notify
```

After `score` finishes successfully, both `load` and `notify` are eligible to run. The failure of `notify` on its first two attempts does not mean that `score` has failed, and it also does not mean that `load` has failed. The two tasks are separate branches that only share the same upstream dependency.

In this run, `notify` was deliberately made to fail twice. Those 2 failures were handled by the retry mechanism rather than the whole process failing immediately. Since `load` does not depend on `notify`, the `load` task can still execute independently after `score` has completed successfully.

This shows that a failure in one branch of a DAG would not automatically affect another unrelated branch. A task should affect the execution of tasks that depend on it, but a sibling task should not be considered failed just because another sibling failed. This is one of the advantages of representing the workflow as a dependency based DAG instead of sequential execution of tasks one after another.

## Retry cost under FinOps

<!-- Tying back to this week's FinOps content: if notify were a metered API
     call you paid for per attempt, what would you change about the retry
     strategy, and why is "retry every failed task the same way" a risky
     default once cost enters the picture? -->

If `notify` were a metered API call where every attempt had a cost, I would not use the same retry strategy for every task. The retry policy should depend on the type of task, the reason why it can fail, and the cost of performing another attempt.

I would use a **limited number of retries** for metered operations and make the retry policy specific to the task. I would also consider using **increasing delays between retries** rather than immediately retrying every failure. This would reduce unnecessary requests when an external service is temporarily unavailable.

Another important consideration is that retries should be used mainly for failures that are expected to be temporary. A task that is known to fail because of a permanent error should be allowed to fail without repeatedly spending resources on the same operation.

This is why "retry every failed task the same way" is a risky default once cost is involved. Two tasks can have completely different costs and failure characteristics. A cheap local computation may be safe to retry several times, while an external API call that is charged per request could become expensive if it is retried unnecessarily.

## My Approach

I initially completed the setup instructions mentioned in the README. I created the virtual environment, installed the required dependencies and generated the personalized fixtures using my student ID `142301002`. I also recorded the student ID and the generated seed in `NOTES.md`.

The first function I implemented was `topological_order()`. I implemented Kahn's algorithm for this. I first calculated the in-degree of every task based on the number of dependencies it had. I also maintained the list of tasks that depend on each task. Tasks with an in-degree of zero were initially added to the list of tasks that were ready to execute. After selecting a task, I added it to the result and decreased the in-degree of all tasks that depended on it. When the in-degree of one of those tasks became zero, I added it to the ready list.

While implementing this function, I also handled the two invalid DAG cases mentioned in the README. If a task depended on a task name that did not exist, I raised a `ValueError`. I also checked whether all tasks could be placed in the final ordering. If some tasks were still left after there were no tasks with zero in-degree, it indicated that the dependency graph contained a cycle, so I raised a `ValueError` in that case.

The second function I implemented was `run_task_with_retry()`. The purpose of this function was to execute one task and retry it when it failed. I kept track of the number of attempts made and allowed `max_retries` additional attempts after the first attempt. Therefore, a task with `max_retries` equal to 2 could make a maximum of 3 attempts. If the task succeeded, I returned the number of attempts taken. If the task failed and there were still retries remaining, I waited for the specified `retry_delay_seconds` before trying again. If all attempts failed, I allowed the last exception to propagate instead of hiding it.

The third function was `run_dag()`, which combined the previous two functions to execute the complete DAG. I first obtained the topological ordering using `topological_order()`. I then went through the tasks in that order and passed the corresponding `Task` object and the same `context` dictionary to `run_task_with_retry()`. This allowed information written by one task into the context to be available to downstream tasks. For every successfully completed task, I recorded its status and the number of attempts. If a task failed even after all its retries, I recorded the failure and the error message and stopped the DAG execution so that the tasks after the failed task would not be executed.

After implementing the three functions, I ran the actual pipeline using `python src/run_pipeline.py`. This generated `batch_report.json` and `dag_run_summary.json`. Finally, I used the provided self-check tests to verify the implementation.