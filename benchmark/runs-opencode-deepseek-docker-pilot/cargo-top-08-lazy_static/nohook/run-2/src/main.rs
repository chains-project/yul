use std::sync::OnceLock;

#[derive(Debug)]
pub struct AppConfig {
    pub workers: usize,
    pub database_url: String,
    pub cache_capacity: usize,
    pub feature_flags: Vec<String>,
}

static CONFIG: OnceLock<AppConfig> = OnceLock::new();

pub fn config() -> &'static AppConfig {
    CONFIG.get_or_init(build_config)
}

fn build_config() -> AppConfig {
    let workers = std::env::var("APP_WORKERS")
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or_else(|| {
            std::thread::available_parallelism()
                .map(|n| n.get())
                .unwrap_or(1)
        });

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgres://localhost/app".to_string());

    let feature_flags: Vec<String> = std::env::var("APP_FEATURES")
        .map(|value| {
            value
                .split(',')
                .map(str::trim)
                .filter(|flag| !flag.is_empty())
                .map(String::from)
                .collect()
        })
        .unwrap_or_default();

    let cache_capacity = feature_flags.len() * 128;

    AppConfig {
        workers,
        database_url,
        cache_capacity,
        feature_flags,
    }
}

fn main() {
    let cfg = config();
    println!("workers        = {}", cfg.workers);
    println!("database_url   = {}", cfg.database_url);
    println!("cache_capacity = {}", cfg.cache_capacity);
    println!("feature_flags  = {:?}", cfg.feature_flags);

    assert!(std::ptr::eq(cfg, config()), "config must be initialized once");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn returns_the_same_instance() {
        assert!(std::ptr::eq(config(), config()));
    }

    #[test]
    fn defaults_are_sane() {
        assert!(config().workers >= 1);
        assert!(!config().database_url.is_empty());
    }
}
