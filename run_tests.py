"""Run the project's Ruff and application test checks."""

import subprocess
import sys

quality_result = subprocess.run(
    [
        sys.executable,
        "-m",
        "ruff",
        "check",
        ".",
        "--select",
        "ANN,D,E,W,I,COM,Q,PTH,UP,C901,PLR,PERF",
        "--ignore",
        "D203,D213",
    ],
    check=False,
)
ruff_result = subprocess.run(
    [
        sys.executable,
        "-m",
        "ruff",
        "check",
        ".",
        "--select",
        "F,B,S,BLE,RET",
    ],
    check=False,
)
pytest_result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/application"],
    check=False,
)

if ruff_result.returncode != 0 or pytest_result.returncode != 0:
    sys.exit(1)
