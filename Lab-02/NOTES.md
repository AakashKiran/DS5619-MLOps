# NOTES.md — Week 2: Config-Driven Data Pipelines

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
- 142301002
- Seed Generated : 2152466865 

## What was hardcoded, and what would switching it have required?

<!-- What specifically was hardcoded in the original script, and what would
     have had to happen to change the threshold or switch formats before
     your refactor? -->

In `pipeline_hardcoded.py` - input_path, high_value_threshold and output_path were hardcoded. It also works only if the input data is of csv format as it uses only csv.DictReader method to read the input file. 

Before this refactor, any switch would require:
* Any change to high_value_threshold needs to reflect in pipeline_hardcoded.py (manual updation).
* Any format change needs additional code to be written to specifically cater to it (csv.DictReader works well for only csv files). 
* Since both these changes are to be made in source code, someone with technical knowledge would be required to make changes and also complete re-deployment of the code would be needed. 

Instead, if a configuration file is maintained, these changes can be made quickly without having to re-deploy and making changes doesn't require someone who knows coding making the whole process easier and efficient. 