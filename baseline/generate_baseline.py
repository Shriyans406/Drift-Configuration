import os
import json
import hashlib
from datetime import datetime

CONFIG_FILES = [
    "/etc/nginx/nginx.conf",
    "/etc/ssh/sshd_config"
]

def generate_hash(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def read_file_content(file_path):
    with open(file_path, "r") as f:
        return f.read()

def create_baseline():
    baseline_data = {}

    for file in CONFIG_FILES:
        if os.path.exists(file):
            try:
                file_hash = generate_hash(file)
                content = read_file_content(file)
                timestamp = datetime.now().isoformat()

                baseline_data[file] = {
                    "hash": file_hash,
                    "content": content,
                    "timestamp": timestamp
                }

                print(f"[OK] Processed: {file}")

            except Exception as e:
                print(f"[ERROR] Could not read {file}: {e}")
        else:
            print(f"[WARNING] File not found: {file}")

    return baseline_data

def save_baseline(data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "../data/baseline.json")

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nBaseline saved to {output_path}")

if __name__ == "__main__":
    print("Generating baseline...\n")

    baseline = create_baseline()
    save_baseline(baseline)

    print("\nDone.")                
