use std::collections::HashMap;
use std::env;
use std::sync::LazyLock;

/// Application configuration, computed at runtime on first access.
#[derive(Debug)]
pub struct Config {
    pub app_name: String,
    pub worker_threads: usize,
    pub lookup: HashMap<&'static str, u32>,
}

/// Global config. The closure runs exactly once, on first dereference,
/// and is thread-safe; every later access returns the same value.
pub static CONFIG: LazyLock<Config> = LazyLock::new(|| {
    let app_name = env::var("APP_NAME").unwrap_or_else(|_| "app".to_string());

    let worker_threads = env::var("APP_WORKERS")
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

    Config {
        app_name,
        worker_threads,
        lookup,
    }
});

fn main() {
    println!("app_name:       {}", CONFIG.app_name);
    println!("worker_threads: {}", CONFIG.worker_threads);
    println!("lookup[beta]:   {:?}", CONFIG.lookup.get("beta"));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initializes_once_and_is_shared() {
        let a: &Config = &CONFIG;
        let b: &Config = &CONFIG;
        assert!(std::ptr::eq(a, b));
        assert!(CONFIG.worker_threads >= 1);
        assert_eq!(CONFIG.lookup.get("gamma"), Some(&3));
    }
}
