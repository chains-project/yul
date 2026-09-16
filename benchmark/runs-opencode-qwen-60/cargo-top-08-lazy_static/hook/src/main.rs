use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref CONFIG_MAP: HashMap<&'static str, String> = {
        let mut m = HashMap::new();
        m.insert("app_name", "LazyStaticApp".to_string());
        m.insert("version", "0.1.0".to_string());
        m.insert("debug_mode", "true".to_string());
        m
    };

    static ref COMPUTED_HASH: u64 = compute_hash();
}

fn compute_hash() -> u64 {
    let data = "initial seed data";
    let mut hash: u64 = 0;
    for c in data.chars() {
        hash = hash.wrapping_mul(31).wrapping_add(c as u64);
    }
    hash
}

fn get_config(key: &str) -> Option<&String> {
    CONFIG_MAP.get(key)
}

fn main() {
    println!("App: {}", get_config("app_name").unwrap());
    println!("Version: {}", get_config("version").unwrap());
    println!("Debug: {}", get_config("debug_mode").unwrap());
    println!("Computed hash: {}", *COMPUTED_HASH);
}