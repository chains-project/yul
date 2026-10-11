use std::collections::HashMap;
use std::sync::LazyLock;

static CONFIG: LazyLock<HashMap<String, u32>> = LazyLock::new(|| {
    println!("computing CONFIG once...");
    let mut map = HashMap::new();
    map.insert("workers".to_string(), num_cpus());
    map.insert("max_retries".to_string(), compute_default_retries());
    map
});

fn num_cpus() -> u32 {
    std::thread::available_parallelism()
        .map(|n| n.get() as u32)
        .unwrap_or(1)
}

fn compute_default_retries() -> u32 {
    let base = std::env::var("APP_BASE_RETRIES").unwrap_or_else(|_| "3".to_string());
    base.parse().unwrap_or(3) * 2
}

fn main() {
    println!("workers = {}", CONFIG["workers"]);
    println!("max_retries = {}", CONFIG["max_retries"]);

    println!("workers again = {}", CONFIG["workers"]);
}
