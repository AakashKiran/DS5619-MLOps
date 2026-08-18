"""
The "after" version — YOUR file to complete.

Fill in the three functions marked with # TODO. Everything else (CLI wiring,
imports) is already done for you. Do not hardcode any path, format string, or
threshold value anywhere in this file — if you find yourself typing a literal
number or file path outside of a default/example, it belongs in the config
file instead.

Run with:
    python src/pipeline.py --config config/pipeline.yaml
"""
import argparse
import csv
import json
from pathlib import Path

import yaml

REQUIRED_KEYS = ["input_path", "input_format", "high_value_threshold", "output_path"]


def load_config(path):
    """Load a YAML config file and validate required keys are present.

    Must raise ValueError naming the specific missing key if REQUIRED_KEYS
    are not all present. Do not let this fail with a bare KeyError later.
    """
    # TODO: implement
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    keys = list(data.keys())
    missing = []
    missing_value = []
    for i in REQUIRED_KEYS:
        if i not in keys:
            missing.append(i)
        elif data[i] is None:
            missing_value.append(i)
    if len(missing) != 0:
        raise ValueError(f"{missing} is/are the missing keys.")
    if len(missing_value) != 0:
        raise ValueError(f"{missing_value} is/are the keys without values.")
    return data

def load_transactions(path, fmt):
    """Load transactions from `path`, using `fmt` ("csv" or "json") to decide
    how to parse it — not by sniffing the file extension.

    Must return a list of dicts. Every dict must have at least "amount"
    (str or float) and "is_fraud" (str "True"/"False" or bool).
    Raise ValueError for any fmt other than "csv" or "json".
    """
    # TODO: implement
    file_extension = Path(path).suffix.lower()    
    if fmt == "csv" and file_extension != ".csv":
        raise ValueError(f"Config format is 'csv', but file extension is '{file_extension}'")
    if fmt == "json" and file_extension != ".json":
        raise ValueError(f"Config format is 'json', but file extension is '{file_extension}'")
    
    if fmt == "csv":
        try:
            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception:
            raise Exception(f"Could not find (or) Failed to read the CSV file at: {path}")
    elif fmt == "json":
        try:
            with open(path, newline="") as file:
                data = json.load(file)
                return data
        except Exception:
            raise Exception(f"Could not find (or) Failed to read the JSON file at: {path}")
    else:
        raise ValueError(f"{fmt} is neither csv nor json.")        

def run_pipeline(config):
    """Load data per `config`, compute the same summary fields as
    pipeline_hardcoded.py (n_transactions, total_amount, fraud_rate,
    n_high_value, high_value_threshold), and write them as JSON to
    config["output_path"]. Return the report dict as well.
    """
    # TODO: implement
    rows = load_transactions(config["input_path"], config["input_format"])
    n = len(rows)
    total_amount = sum(float(r["amount"]) for r in rows)
    n_fraud = sum(1 for r in rows if str(r["is_fraud"]).lower() == "true")
    n_high_value = sum(1 for r in rows if float(r["amount"]) > config["high_value_threshold"])

    report = {
        "n_transactions": n,
        "total_amount": round(total_amount, 2),
        "fraud_rate": round(n_fraud / n, 4) if n else 0.0,
        "n_high_value": n_high_value,
        "high_value_threshold": config["high_value_threshold"],
    }

    with open(config["output_path"], "w") as f:
        json.dump(report, f, indent=2)

    print(f"Wrote report to {config['output_path']}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Config-driven fraud transaction summary pipeline")
    parser.add_argument("--config", required=True, help="Path to a YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)
    report = run_pipeline(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
