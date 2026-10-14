use std::collections::HashMap;
use std::env;
use std::sync::LazyLock;

/// Application configuration computed once at runtime.
///
/// `LazyLock` (stable since Rust 1.80) runs the closure on first access,
/// is thread-safe, and caches the result for every later access, so the
/// value can depend on things a `const`/plain `static` can't: env vars,
/// heap allocation, file I/O, and so on.
static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

/// A lookup table built at runtime from heap-allocated data.
static SQUARES: LazyLock<HashMap<u32, u64>> =
    LazyLock::new(|| (1..=10).map(|n| (n, u64::from(n) * u64::from(n))).collect());

#[derive(Debug)]
struct Config {
    app_name: String,
    worker_count: usize,
}

impl Config {
    fn from_env() -> Self {
        Self {
            app_name: env::var("APP_NAME").unwrap_or_else(|_| "app".to_string()),
            worker_count: env::var("APP_WORKERS")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or_else(|| {
                    std::thread::available_parallelism().map_or(1, |n| n.get())
                }),
        }
    }
}

fn main() {
    println!("{} running with {} workers", CONFIG.app_name, CONFIG.worker_count);
    println!("7 squared is {}", SQUARES[&7]);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn squares_table_is_populated() {
        assert_eq!(SQUARES.len(), 10);
        assert_eq!(SQUARES[&10], 100);
    }

    #[test]
    fn config_is_initialized_once() {
        let a: *const Config = &*CONFIG;
        let b: *const Config = &*CONFIG;
        assert_eq!(a, b);
        assert!(CONFIG.worker_count >= 1);
    }
}
