use std::collections::HashMap;
use std::sync::LazyLock;

static CONFIG: LazyLock<HashMap<String, String>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    map.insert("app_name".to_string(), env!("CARGO_PKG_NAME").to_string());
    map.insert(
        "log_level".to_string(),
        std::env::var("LOG_LEVEL").unwrap_or_else(|_| "info".to_string()),
    );
    map.insert(
        "worker_count".to_string(),
        std::thread::available_parallelism()
            .map(|n| n.get().to_string())
            .unwrap_or_else(|_| "1".to_string()),
    );
    println!("initializing CONFIG...");
    map
});

fn main() {
    println!("app_name = {}", CONFIG["app_name"]);
    println!("log_level = {}", CONFIG["log_level"]);
    println!("worker_count = {}", CONFIG["worker_count"]);

    let first = &*CONFIG;
    let second = &*CONFIG;
    assert!(std::ptr::eq(first, second));
    println!("CONFIG initialized once, reused thereafter");
}
