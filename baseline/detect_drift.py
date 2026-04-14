import os
import json
import hashlib
CONFIG_FILES = [
    "/etc/ssh/sshd_config",
    "/etc/hosts"
]
def generate_hash(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def load_baseline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "../data/baseline.json")

    if not os.path.exists(path):
        print("[ERROR] Baseline file not found!")
        return None

    with open(path, "r") as f:
        return json.load(f)

def get_current_hashes():
    current_data = {}

    for file in CONFIG_FILES:
        if os.path.exists(file):
            try:
                current_data[file] = generate_hash(file)
                print(f"[OK] Current hash generated: {file}")
            except Exception as e:
                print(f"[ERROR] Could not read {file}: {e}")
        else:
            print(f"[WARNING] File missing: {file}")

    return current_data

def detect_drift(baseline, current):
    changed_files = []

    for file in baseline:
        old_hash = baseline[file]["hash"]
        new_hash = current.get(file)

        if new_hash is None:
            print(f"[ALERT] File missing now: {file}")
            changed_files.append(file)
        elif old_hash != new_hash:
            print(f"[DRIFT] File changed: {file}")
            changed_files.append(file)
        else:
            print(f"[OK] No change: {file}")

    return changed_files

if __name__ == "__main__":
    print("Checking for configuration drift...\n")

    baseline = load_baseline()

    if baseline is None:
        exit()

    current = get_current_hashes()

    changed = detect_drift(baseline, current)

    print("\nSummary:")
    if changed:
        print("Changed files detected:")
        for f in changed:
            print(f" - {f}")
    else:
        print("No drift detected. System is stable.")