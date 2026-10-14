use std::collections::HashMap;
use std::env;
use std::sync::LazyLock;

/// Application configuration, computed once at runtime on first access.
///
/// `LazyLock` (std, Rust 1.80+) runs the closure exactly once, thread-safely,
/// the first time `CONFIG` is dereferenced. Later accesses return the cached value.
static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

#[derive(Debug)]
struct Config {
    app_name: String,
    worker_count: usize,
    lookup: HashMap<&'static str, u32>,
}

impl Config {
    fn from_env() -> Self {
        let worker_count = env::var("APP_WORKERS")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or_else(|| {
                std::thread::available_parallelism()
                    .map(|n| n.get())
                    .unwrap_or(1)
            });

        let lookup = [("alpha", 1), ("beta", 2), ("gamma", 3)]
            .into_iter()
            .collect();

        Self {
            app_name: env::var("APP_NAME").unwrap_or_else(|_| "app".to_string()),
            worker_count,
            lookup,
        }
    }
}

fn main() {
    println!("app_name     = {}", CONFIG.app_name);
    println!("worker_count = {}", CONFIG.worker_count);
    println!("beta         = {:?}", CONFIG.lookup.get("beta"));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn config_is_initialized_once() {
        let a: *const Config = &*CONFIG;
        let b: *const Config = &*CONFIG;
        assert_eq!(a, b);
        assert!(CONFIG.worker_count >= 1);
        assert_eq!(CONFIG.lookup.get("gamma"), Some(&3));
    }
}
