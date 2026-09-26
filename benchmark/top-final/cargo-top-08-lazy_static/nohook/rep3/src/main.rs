use std::collections::HashMap;
use std::sync::LazyLock;

/// Global lookup table built once, on first access, from values only known at runtime.
static CONFIG: LazyLock<HashMap<String, String>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    for (key, value) in std::env::vars() {
        map.insert(key, value);
    }
    map.insert("started_at".to_string(), format!("{:?}", std::time::SystemTime::now()));
    map
});

fn main() {
    println!("loaded {} config entries", CONFIG.len());
    if let Some(started_at) = CONFIG.get("started_at") {
        println!("started_at = {started_at}");
    }
}
