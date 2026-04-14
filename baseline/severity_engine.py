import os
import json
import difflib

def load_baseline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "../data/baseline.json")

    if not os.path.exists(path):
        print("[ERROR] Baseline not found!")
        return None

    with open(path, "r") as f:
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

        # SSH config changes → HIGH
        if "sshd_config" in file:
            severity = "HIGH"
            reason = "SSH configuration changed"
            break

        # Port-related changes → HIGH
        if "port" in line:
            severity = "HIGH"
            reason = "Network port modified"
            break

        # Authentication-related → HIGH
        if "password" in line or "auth" in line:
            severity = "HIGH"
            reason = "Authentication settings changed"
            break

        # Hosts file → LOW (for now)
        if "/etc/hosts" in file:
            severity = "LOW"
            reason = "Hosts file updated"

    return severity, reason

def analyze_with_severity(baseline):
    for file in baseline:
        print(f"\nAnalyzing: {file}")

        old_content = baseline[file]["content"]
        new_content = read_current_file(file)

        if new_content is None:
            print("[ERROR] File missing!")
            continue

        changes = generate_diff(old_content, new_content)

        if changes:
            severity, reason = classify_severity(file, changes)

            print(f"Severity: {severity}")
            print(f"Reason: {reason}")
            print("Changes:")

            for change in changes:
                print(change)
        else:
            print("No changes.")

if __name__ == "__main__":
    print("Running severity analysis...\n")

    baseline = load_baseline()

    if baseline is None:
        exit()

    analyze_with_severity(baseline)

    print("\nDone.")