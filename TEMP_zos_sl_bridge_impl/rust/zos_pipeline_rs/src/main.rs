use zos_pipeline_rs::resonance_score;

fn main() {
    let sample = b"tenant mould complaint";
    let score = resonance_score(sample, 3);
    println!("{}", serde_json::to_string_pretty(&score).unwrap());
}
