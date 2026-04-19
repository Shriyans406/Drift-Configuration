import os
import json
import hashlib
import difflib
from datetime import datetime
import subprocess
import json

CONFIG_FILES = [
    "/etc/ssh/sshd_config",
    "/etc/hosts"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(BASE_DIR, "data/baseline.json")
LOG_PATH = os.path.join(BASE_DIR, "logs/drift.log")

def generate_hash(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        print("[ERROR] Baseline not found!")
        return None

    with open(BASELINE_PATH, "r") as f:
        return json.load(f)

def read_current_file(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return f.readlines()

def generate_diff(old_content, new_content):
    old_lines = old_content.splitlines()
    new_lines = [line.strip("\n") for line in new_content]

    diff = difflib.unified_diff(old_lines, new_lines, lineterm="")

    changes = []

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            changes.append("[ADDED] " + line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            changes.append("[REMOVED] " + line[1:])

    return changes

def classify_severity(file, changes):
    severity = "LOW"
    reason = "Minor changes"

    for change in changes:
        line = change.lower()

        if "sshd_config" in file:
            return "HIGH", "SSH configuration changed"

        if "port" in line:
            return "HIGH", "Network port modified"

        if "password" in line or "auth" in line:
            return "HIGH", "Authentication settings changed"

        if "/etc/hosts" in file:
            severity = "LOW"
            reason = "Hosts file updated"

    return severity, reason

def log_output(message):
    with open(LOG_PATH, "a") as log_file:
        log_file.write(message + "\n")

#newly added
def run_rust_engine():
    print("[DEBUG] Running Rust binary...")

    result = subprocess.run(
        ["./rust_engine/target/debug/rust_engine"],
        capture_output=True,
        text=True
    )

    print("[DEBUG] Return code:", result.returncode)
    print("[DEBUG] STDOUT:", result.stdout)
    print("[DEBUG] STDERR:", result.stderr)

    return result.stdout

def run_pipeline():
    baseline = load_baseline()

    if baseline is None:
        return

    for file in CONFIG_FILES:
        print(f"\nChecking: {file}")

        if file not in baseline:
            print("[WARNING] File not in baseline, skipping")
            continue

        old_content = baseline[file]["content"]
        new_content = read_current_file(file)

        if new_content is None:
            print("[ERROR] File missing!")
            continue

        changes = generate_diff(old_content, new_content)

        if changes:
            severity, reason = classify_severity(file, changes)

            output = f"""
=== DRIFT DETECTED ===
File: {file}
Severity: {severity}
Reason: {reason}
Time: {datetime.now()}

Changes:
{chr(10).join(changes)}
======================
"""
            print(output)
            log_output(output)
        else:
            print("No changes.")

if __name__ == "__main__":
    print("Starting Config Drift Detector...\n")

    #newly added
output = run_rust_engine()

try:
    data = json.loads(output)

    for entry in data:
        if entry["drift"]:
            print(f"\n[DRIFT] {entry['file']}")
            for change in entry["changes"]:
                print(change)

except Exception as e:
    print("Error parsing Rust output:", e)

log_output(output)

print("\nDone.")