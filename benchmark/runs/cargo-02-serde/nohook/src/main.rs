use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Person {
    name: String,
    age: u32,
    email: String,
}

fn main() {
    let input = r#"{"name": "Ada Lovelace", "age": 36, "email": "ada@example.com"}"#;

    let person: Person = serde_json::from_str(input).expect("failed to parse JSON");
    println!("Parsed: {:?}", person);

    let output = serde_json::to_string_pretty(&person).expect("failed to generate JSON");
    println!("Generated:\n{}", output);
}
