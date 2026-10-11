use std::sync::LazyLock;

struct Config {
    greeting: String,
    worker_count: usize,
}

impl Config {
    fn from_env() -> Self {
        let greeting =
            std::env::var("APP_GREETING").unwrap_or_else(|_| "Hello, world!".to_string());
        let worker_count = std::env::var("APP_WORKERS")
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or_else(|| {
                std::thread::available_parallelism()
                    .map(|n| n.get())
                    .unwrap_or(1)
            });
        Config {
            greeting,
            worker_count,
        }
    }
}

static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

fn main() {
    println!("{} ({} workers)", CONFIG.greeting, CONFIG.worker_count);
}
