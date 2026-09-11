use std::collections::HashMap;
use std::sync::LazyLock;

// Initialization needs runtime computation (building a lookup table),
// so it can't be a `const`/`static` literal.
static CONFIG: LazyLock<HashMap<&'static str, u32>> = LazyLock::new(|| {
    let mut m = HashMap::new();
    for (i, name) in ["alpha", "beta", "gamma"].iter().enumerate() {
        m.insert(*name, (i as u32 + 1) * 10);
    }
    m
});

fn main() {
    for (name, value) in [("alpha", 10), ("beta", 20), ("gamma", 30)] {
        println!("{name} = {}", CONFIG[&name]);
        debug_assert_eq!(CONFIG[&name], value);
    }
}
