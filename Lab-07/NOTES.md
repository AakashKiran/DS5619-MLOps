# NOTES.md — Week 7: CI/CD Integration Testing

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- student-id: 142301002
- seed: 2080670810

## Why gate integration-test on needs: [lint, unit-test]?

<!-- Why does integration-test need needs: [lint, unit-test] instead of
     just running in parallel with them — what's the actual cost being
     avoided? -->

The `integration-test` job uses `needs: ["lint", "unit-test"]` so that it runs only after the lint and unit tests have passed.

The integration test is more expensive because it builds and runs a Docker container and performs HTTP-based checks against the running application, which requires additional time and compute resources. In comparison, the lint and unit tests are relatively cheaper and can catch more fundamental issues like code-quality and functionality issues earlier in the pipeline.

Using `needs` prevents the integration test from running when either the lint or unit tests fail. This avoids unnecessarily building and running the Docker container when earlier checks have already identified a problem, thereby saving CI runner time and Docker resources and making the overall CI pipeline more efficient.

## My Approach

Initially I completed the instructions mentioned in the setup section of README.md. This involved creating the virtual environment, installing the required dependencies inside it and generating the custom dataset using my student ID. The generated fixture data was used for testing the application.

I then completed the CI workflow in `.github/workflows/week7_ci.yml`. The workflow was designed with three jobs:

- `lint` - This job checks the code quality using `flake8`. It installs the required dependencies and runs `flake8 src/` to identify coding errors and style issues.
- `unit-test` - This job runs the existing test cases using `pytest tests/`. These tests verify the functionality of the application at the unit-test level.
- `integration-test` - This job runs only after the `lint` and `unit-test` jobs have passed, using `needs: ["lint", "unit-test"]`. It performs an end-to-end test of the application inside a Docker container.

I then implemented `scripts/integration_test.sh` to automate the Docker-based integration test. The script follows these steps:

- It uses `set -euo pipefail` so that the script stops when an error occurs and handles unset variables and failed commands safely.
- It builds the Docker image using `docker build`.
- It repeatedly checks the `/health` endpoint using `curl` until the application becomes ready. If the application does not become ready within the specified number of attempts, the  test fails.
- Once the application is ready, it sends the generated fixture image `data/fixtures/camera_A_daylight/000.jpg` to the `/detect` endpoint using `curl`.
- It verifies that the response contains `"detections"`, confirming that the detection endpoint is responding as expected.
- Finally, a cleanup function removes the Docker container after the test, including when the script exits due to an error.

I first tested the integration script locally after enabling Docker integration with WSL. The script successfully built the image, started the container, passed the health check and successfully tested the `/detect` endpoint. I also ran `pytest tests/ -q`, which resulted in all 12 tests passing.

For the GitHub Actions workflow, the workflow file was initially placed inside `Lab-07/.github/workflows/`, so GitHub Actions did not detect it. I moved it to the repository-level `.github/workflows/week7_ci.yml`. After this, the workflow was detected, but the jobs initially failed because they were running from the repository root instead of the `Lab-07` directory. I therefore set `Lab-07` as the default working directory in the workflow.

After these changes, the workflow was pushed to GitHub and successfully executed all three jobs: `lint`, `unit-test` and `integration-test`. The final GitHub Actions run completed successfully, confirming that the CI pipeline works on a real GitHub Actions runner.