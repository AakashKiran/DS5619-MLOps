# CI verification

Fill this in after you push and watch the workflow run on GitHub (Actions
tab of your repo). This is how we confirm your CI actually ran green in a
real GitHub Actions runner, not just locally.

## Workflow run

Paste the URL of a successful run of all three jobs (Actions tab -> click
the run -> copy the URL):

```
https://github.com/AakashKiran/DS5619-MLOps/actions/runs/35901049701
```

## Job summary

For each job, note pass/fail and how long it took:

- `lint`: pass in 17s
- `unit-test`: pass in 11s
- `integration-test`: pass in 29s

## What broke on the way there (optional but useful)

If any job failed before you got it working, briefly note what the failure
was and what fixed it. (Not required, but if `integration-test` gave you
trouble, this is worth 2 sentences for your own future reference — Week 9's
lab also builds on debugging CI-style failures.)

- Initially when the workflow file was placed inside Lab-07/.github/workflows/, GitHub Actions did not detect it. So it was moved to the repository root at .github/workflows/.
- After moving the workflow to the repository root, the CI jobs initially failed because they were running from the repository root instead of Lab-07. Setting Lab-07 as the default working directory fixed the issue, and all three jobs passed successfully.
