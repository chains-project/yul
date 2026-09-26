use std::collections::HashMap;
use std::sync::LazyLock;

static CONFIG: LazyLock<HashMap<&'static str, String>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    map.insert("hostname", hostname());
    map.insert("started_at", std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
        .to_string());
    map
});

fn hostname() -> String {
    std::env::var("HOSTNAME").unwrap_or_else(|_| "unknown".to_string())
}

fn main() {
    println!("hostname: {}", CONFIG["hostname"]);
    println!("started_at: {}", CONFIG["started_at"]);
}
