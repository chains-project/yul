//! Global, lazily-initialized application configuration.
//!
//! `CONFIG` can't be a `const` or a plain `static` initializer because its
//! value depends on runtime information (environment variables, CPU count,
//! process start time). `LazyLock` runs the initializer exactly once, on first
//! access, and is safe to read from any number of threads afterwards.

use std::env;
use std::sync::LazyLock;
use std::thread;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

#[derive(Debug)]
pub struct Config {
    pub app_name: String,
    pub worker_threads: usize,
    pub debug: bool,
    pub started_at: Instant,
    pub started_unix_secs: u64,
}

pub static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

impl Config {
    fn from_env() -> Self {
        let default_workers = thread::available_parallelism().map_or(1, |n| n.get());

        Self {
            app_name: env::var("APP_NAME").unwrap_or_else(|_| "app".to_string()),
            worker_threads: env::var("APP_WORKERS")
                .ok()
                .and_then(|v| v.parse().ok())
                .filter(|&n| n > 0)
                .unwrap_or(default_workers),
            debug: matches!(env::var("APP_DEBUG").as_deref(), Ok("1" | "true")),
            started_at: Instant::now(),
            started_unix_secs: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_or(0, |d| d.as_secs()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initialized_once_and_shared_across_threads() {
        let addr = &*CONFIG as *const Config as usize;
        let handles: Vec<_> = (0..8)
            .map(|_| thread::spawn(|| &*CONFIG as *const Config as usize))
            .collect();
        for h in handles {
            assert_eq!(h.join().unwrap(), addr);
        }
    }

    #[test]
    fn worker_threads_is_positive() {
        assert!(CONFIG.worker_threads > 0);
    }
}
