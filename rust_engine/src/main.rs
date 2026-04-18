use std::fs;
use std::collections::HashMap;
use serde::Deserialize;

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

fn main() {
    let baseline_path = "../data/baseline.json";

    let baseline = load_baseline(baseline_path);

    println!("Running Rust Drift Engine...\n");

    for (file, data) in baseline.iter() {
        println!("Checking: {}", file);

        let current_content = match fs::read_to_string(file) {
            Ok(content) => content,
            Err(_) => {
                println!("[ERROR] Cannot read file\n");
                continue;
            }
        };

        let current_hash = generate_hash(file);

        if current_hash != data.hash {
            println!("DRIFT DETECTED!");

            let changes = generate_diff(&data.content, &current_content);

            for change in changes {
                println!("{}", change);
            }
        } else {
            println!("No change.");
        }

        println!();
    }
}