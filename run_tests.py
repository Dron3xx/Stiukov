import sys
import subprocess

ruff_result = subprocess.run(["ruff", "check", "."])
pytest_result = subprocess.run(["pytest"])

if ruff_result.returncode != 0 or pytest_result.returncode != 0:
    sys.exit(1)