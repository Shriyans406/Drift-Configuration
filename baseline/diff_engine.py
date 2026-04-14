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

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm=""
    )

    changes = []

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            changes.append("[ADDED] " + line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            changes.append("[REMOVED] " + line[1:])

    return changes

def analyze_changes(baseline):
    for file in baseline:
        print(f"\nChecking: {file}")

        old_content = baseline[file]["content"]
        new_content = read_current_file(file)

        if new_content is None:
            print("[ERROR] File missing!")
            continue

        changes = generate_diff(old_content, new_content)

        if changes:
            print("Changes detected:")
            for change in changes:
                print(change)
        else:
            print("No changes.")

if __name__ == "__main__":
    print("Running diff engine...\n")

    baseline = load_baseline()

    if baseline is None:
        exit()

    analyze_changes(baseline)

    print("\nDone.")