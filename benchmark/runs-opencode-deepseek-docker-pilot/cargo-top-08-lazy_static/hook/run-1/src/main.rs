use std::collections::HashMap;
use std::env;
use std::sync::{LazyLock, OnceLock};

// A `static` normally needs a const-evaluable initializer. `LazyLock` lifts
// that restriction: the closure runs at runtime, exactly once, on first
// dereference. Every later access reuses the cached value.
static HTTP_STATUS_CODES: LazyLock<HashMap<u16, &'static str>> = LazyLock::new(|| {
    println!("initializing HTTP_STATUS_CODES (this runs once)");

    let mut map = HashMap::new();
    for (code, reason) in [
        (200u16, "OK"),
        (301, "Moved Permanently"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
    ] {
        map.insert(code, reason);
    }
    map
});

// When initialization depends on runtime input or can fail, use `OnceLock`
// and compute the value in a normal function via `get_or_init`.
static WORKER_THREADS: OnceLock<usize> = OnceLock::new();

fn worker_threads() -> usize {
    *WORKER_THREADS.get_or_init(|| {
        env::var("WORKER_THREADS")
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or_else(|| {
                std::thread::available_parallelism()
                    .map(|n| n.get())
                    .unwrap_or(1)
            })
    })
}

fn main() {
    // Both lookups share a single initialization.
    println!("200 -> {}", HTTP_STATUS_CODES.get(&200).unwrap());
    println!("404 -> {}", HTTP_STATUS_CODES.get(&404).unwrap());

    println!("worker threads: {}", worker_threads());
    println!("worker threads: {}", worker_threads());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn table_is_populated() {
        assert_eq!(HTTP_STATUS_CODES.get(&500), Some(&"Internal Server Error"));
    }

    #[test]
    fn threads_always_default_to_at_least_one() {
        assert!(worker_threads() >= 1);
    }
}
