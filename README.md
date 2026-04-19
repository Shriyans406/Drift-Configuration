# Config Drift Detector

## Objective
The Config Drift Detector is a security and compliance tool designed to monitor critical system configuration files for unauthorized or unexpected modifications (drifts). By comparing the current state of configuration files against a known good baseline, it helps system administrators identify changes that could signify security risks, misconfigurations, or policy violations.

## What It Does
The tool actively monitors specific configuration files on Linux-based systems (by default, `/etc/ssh/sshd_config` and `/etc/hosts`). When a change is detected, the tool:
1. Identifies the specific lines added or removed.
2. Classifies the severity of the modification (e.g., changes to SSH ports or authentication methods are flagged as HIGH severity, whereas modifications to host entries are flagged as LOW severity).
3. Logs the drift details into a log file for auditing purposes.

## How It Works
The architecture utilizes a dual-engine approach combining Python and Rust for both scriptable logic and high-performance verification:

### 1. Python Engine (main.py)
The primary orchestrator and entry point. 
- It loads a predefined JSON baseline containing expected configurations and their MD5 hashes.
- It parses the live configuration files and computes the exact differences line by line.
- It applies business rules to classify the severity of the drift based on keywords and file paths.
- It logs the results to `logs/drift.log` and outputs the findings to the console.
- It acts as a wrapper by invoking the Rust Engine to perform secondary drift detection validations.

### 2. Rust Engine (rust_engine/src/main.rs)
A high-performance validation component.
- The Rust binary reads the same baseline JSON data.
- It computes a live MD5 hash of the current files and efficiently compares them against the baseline hashes.
- Upon mismatch, it generates a diff showing added and removed lines.
- It serializes the drift report into a JSON format and passes it back to the Python orchestrator via standard output.

### 3. Data & Scripts
- **Baseline Data**: Managed within `data/baseline.json`. Contains the expected hashes, file content, and the timestamp of creation.
- **Run Script**: `scripts/run_detector.sh` is provided as a convenient execution wrapper.

## Prerequisites and Installation
To install and run the Config Drift Detector, ensure your system meets the following requirements:

### Requirements
- **OS**: Linux (requires the ability to read system `/etc` directories, therefore typically ran as root/sudo).
- **Python**: Python 3.x installed.
- **Rust**: The Rust toolchain (cargo, rustc) must be installed to compile the Rust Engine.

### Setup and Compilation
1. Clone or navigate to the repository directory.
2. Build the Rust Engine component:
   ```bash
   cd rust_engine
   cargo build
   cd ..
   ```
   *Note: Ensure you build it in standard debug mode or adjust the Python script to point to the release binary if you build with `--release`.*
3. Ensure the log directory exists (if not, you can create it):
   ```bash
   mkdir -p logs
   ```

## How to Conduct the Job (Usage)

To run the drift detector and check your system files based on the baseline configuration, you can use the provided shell script or run the Python script directly. Because the tool reads protected system configuration files like `/etc/ssh/sshd_config`, it must be run with elevated privileges (sudo).

### Method 1: Using the Wrapper Script
Execute the provided bash script to run the job securely:
```bash
sudo ./scripts/run_detector.sh
```

### Method 2: Running the Python script directly
Run the Python orchestrator with sudo:
```bash
sudo python3 main.py
```

## Reviewing the Output
When a drift is discovered, the terminal output will explicitly state the specific alterations, the severity, and the reasoning behind the classification.

Additionally, all findings are permanently logged for audit trails in `logs/drift.log`. You can review historical drifts by inspecting the log file:
```bash
cat logs/drift.log
```
