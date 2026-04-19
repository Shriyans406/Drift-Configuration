use std::fs;
use std::collections::HashMap;
use serde::Deserialize;

use std::env;

use serde::Serialize;


#[derive(Deserialize)]
struct FileData {
    hash: String,
    content: String,
    timestamp: String,
}

fn load_baseline(path: &str) -> HashMap<String, FileData> {
    let data = fs::read_to_string(path)
        .expect("Failed to read baseline.json");

    serde_json::from_str(&data)
        .expect("Failed to parse JSON")
}

fn generate_hash(file_path: &str) -> String {
    let data = fs::read(file_path)
        .expect("Failed to read file");

    format!("{:x}", md5::compute(data))
}

fn generate_diff(old_content: &str, new_content: &str) -> Vec<String> {
    let old_lines: Vec<&str> = old_content.lines().collect();
    let new_lines: Vec<&str> = new_content.lines().collect();

    let mut changes = Vec::new();

    for line in &new_lines {
        if !old_lines.contains(line) {
            changes.push(format!("[ADDED] {}", line));
        }
    }

    for line in &old_lines {
        if !new_lines.contains(line) {
            changes.push(format!("[REMOVED] {}", line));
        }
    }

    changes
}


#[derive(Serialize)]
struct DriftResult {
    file: String,
    drift: bool,
    changes: Vec<String>,
}


fn main() {
    let baseline_path = "/home/vboxuser/projects/config-drift-detector/data/baseline.json";

    let baseline = load_baseline(baseline_path);

    let mut results: Vec<DriftResult> = Vec::new();

    for (file, data) in baseline.iter() {

        let current_content = match fs::read_to_string(file) {
            Ok(content) => content,
            Err(_) => continue,
        };

        let current_hash = generate_hash(file);

        if current_hash != data.hash {
            let changes = generate_diff(&data.content, &current_content);

            results.push(DriftResult {
                file: file.to_string(),
                drift: true,
                changes,
            });
        } else {
            results.push(DriftResult {
                file: file.to_string(),
                drift: false,
                changes: vec![],
            });
        }
    }

    let json_output = serde_json::to_string_pretty(&results).unwrap();
    println!("{}", json_output);
}