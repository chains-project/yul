use std::collections::HashMap;
use std::sync::LazyLock;

static CONFIG: LazyLock<HashMap<&'static str, u64>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    map.insert("sum", (1..=1_000_000).sum());
    map.insert("count", (1..=1_000_000).count() as u64);
    map
});

fn main() {
    println!("sum   = {}", CONFIG["sum"]);
    println!("count = {}", CONFIG["count"]);
}
