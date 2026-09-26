use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref CONFIG: HashMap<&'static str, String> = {
        let mut m = HashMap::new();
        m.insert("hostname", std::env::var("HOSTNAME").unwrap_or_else(|_| "unknown".to_string()));
        m.insert("pid", std::process::id().to_string());
        m
    };
}

fn main() {
    println!("hostname: {}", CONFIG["hostname"]);
    println!("pid: {}", CONFIG["pid"]);
}
