use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    /// Built at first access from environment/host state, so it can't be a `const`.
    static ref CONFIG: HashMap<String, String> = {
        let mut m = HashMap::new();
        m.insert("hostname".to_string(), hostname());
        m.insert("pid".to_string(), std::process::id().to_string());
        m
    };
}

fn hostname() -> String {
    std::env::var("HOSTNAME").unwrap_or_else(|_| "unknown".to_string())
}

fn main() {
    println!("hostname = {}", CONFIG["hostname"]);
    println!("pid = {}", CONFIG["pid"]);
}
