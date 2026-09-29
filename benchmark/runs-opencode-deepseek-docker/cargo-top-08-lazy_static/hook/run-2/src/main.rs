use std::sync::LazyLock;

struct AppConfig {
    name: String,
    workers: usize,
}

fn load_config() -> AppConfig {
    let name = std::env::var("APP_NAME").unwrap_or_else(|_| "runtime-global".to_string());
    let workers = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1);

    AppConfig { name, workers }
}

static CONFIG: LazyLock<AppConfig> = LazyLock::new(load_config);

fn main() {
    println!("app: {}", CONFIG.name);
    println!("workers: {}", CONFIG.workers);
}
