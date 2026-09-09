import subprocess

subprocess.run(["ruff", "check", "."])
subprocess.run(["pytest"])