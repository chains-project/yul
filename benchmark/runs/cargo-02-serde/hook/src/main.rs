use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Person {
    name: String,
    age: u32,
    email: String,
}

fn main() {
    // Parse JSON into a struct
    let data = r#"
        {
            "name": "Ada Lovelace",
            "age": 36,
            "email": "ada@example.com"
        }
    "#;
    let person: Person = serde_json::from_str(data).expect("failed to parse JSON");
    println!("Parsed: {:?}", person);

    // Generate JSON from a struct
    let json = serde_json::to_string_pretty(&person).expect("failed to generate JSON");
    println!("Generated:\n{}", json);
}
