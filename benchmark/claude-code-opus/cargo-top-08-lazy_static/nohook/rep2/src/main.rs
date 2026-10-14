use std::collections::HashMap;
use std::env;
use std::sync::LazyLock;

/// Application configuration, computed at runtime on first access.
///
/// `LazyLock` runs the closure exactly once, the first time `CONFIG` is
/// dereferenced, and is thread-safe: concurrent first accesses block until
/// initialization finishes, and all of them see the same value.
static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

#[derive(Debug)]
pub struct Config {
    pub app_name: String,
    pub worker_threads: usize,
    pub lookup: HashMap<&'static str, u32>,
}

impl Config {
    fn from_env() -> Self {
        let app_name = env::var("APP_NAME").unwrap_or_else(|_| "app".to_string());

        let worker_threads = env::var("APP_WORKERS")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or_else(|| {
                std::thread::available_parallelism()
                    .map(|n| n.get())
                    .unwrap_or(1)
            });

        let lookup = HashMap::from([("alpha", 1), ("beta", 2), ("gamma", 3)]);

        Config {
            app_name,
            worker_threads,
            lookup,
        }
    }
}

fn main() {
    // First access triggers initialization; later accesses reuse the value.
    println!("app_name:       {}", CONFIG.app_name);
    println!("worker_threads: {}", CONFIG.worker_threads);
    println!("lookup[beta]:   {:?}", CONFIG.lookup.get("beta"));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initializes_once_across_threads() {
        let addrs: Vec<usize> = (0..8)
            .map(|_| std::thread::spawn(|| &*CONFIG as *const Config as usize))
            .map(|h| h.join().unwrap())
            .collect();
        assert!(addrs.windows(2).all(|w| w[0] == w[1]));
    }

    #[test]
    fn has_at_least_one_worker() {
        assert!(CONFIG.worker_threads >= 1);
    }
}
