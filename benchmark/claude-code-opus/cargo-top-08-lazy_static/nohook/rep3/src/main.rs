use std::collections::HashMap;
use std::env;
use std::sync::LazyLock;

/// Application configuration computed at runtime on first access.
///
/// `static` items normally require a compile-time constant initializer.
/// `LazyLock` defers the closure until the value is first dereferenced,
/// runs it exactly once (thread-safe), and caches the result for the
/// lifetime of the program.
#[derive(Debug)]
pub struct Config {
    pub app_name: String,
    pub worker_threads: usize,
    pub lookup: HashMap<&'static str, u32>,
}

pub static CONFIG: LazyLock<Config> = LazyLock::new(|| {
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
        app_name: env::var("APP_NAME").unwrap_or_else(|_| "lazy_static_app".to_string()),
        worker_threads,
        lookup,
    }
});

fn main() {
    println!("app name:       {}", CONFIG.app_name);
    println!("worker threads: {}", CONFIG.worker_threads);
    println!("beta lookup:    {:?}", CONFIG.lookup.get("beta"));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initializes_once_and_is_shared() {
        let a: *const Config = &*CONFIG;
        let b: *const Config = &*CONFIG;
        assert_eq!(a, b);
        assert!(CONFIG.worker_threads >= 1);
        assert_eq!(CONFIG.lookup.get("gamma"), Some(&3));
    }
}
