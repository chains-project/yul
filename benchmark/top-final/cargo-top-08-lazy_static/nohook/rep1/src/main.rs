use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    // Building a HashMap isn't something `const`/`static` can do at compile
    // time, so initialization is deferred to first access at runtime.
    static ref CONFIG: HashMap<&'static str, String> = {
        let mut m = HashMap::new();
        m.insert("hostname", hostname());
        m.insert("started_at", std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs()
            .to_string());
        m
    };
}

fn hostname() -> String {
    std::env::var("HOSTNAME").unwrap_or_else(|_| "unknown".to_string())
}

fn main() {
    println!("hostname: {}", CONFIG["hostname"]);
    println!("started_at: {}", CONFIG["started_at"]);
}
