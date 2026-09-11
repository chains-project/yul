use std::collections::HashMap;
use std::env;

use lazy_static::lazy_static;

lazy_static! {
    // Requires runtime work (reading env vars, hashing, etc.) so it can't be a `const`/`static` literal.
    static ref CONFIG: HashMap<String, String> = {
        let mut m = HashMap::new();
        for (key, value) in env::vars() {
            m.insert(key, value);
        }
        m.entry("APP_NAME".to_string())
            .or_insert_with(|| "lazy_static_demo".to_string());
        m
    };
}

fn main() {
    println!("APP_NAME = {}", CONFIG.get("APP_NAME").unwrap());
    println!("Loaded {} environment entries into CONFIG", CONFIG.len());
}
