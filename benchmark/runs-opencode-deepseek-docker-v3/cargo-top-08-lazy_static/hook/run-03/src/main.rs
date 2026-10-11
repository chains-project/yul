use std::collections::HashMap;
use std::sync::LazyLock;

struct Config {
    app_name: String,
    worker_count: usize,
    lookup: HashMap<String, usize>,
}

impl Config {
    fn load() -> Self {
        let app_name = std::env::var("APP_NAME").unwrap_or_else(|_| "runtime_global".to_string());

        let worker_count = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1);

        let lookup = app_name
            .chars()
            .enumerate()
            .map(|(i, c)| (c.to_string(), i))
            .collect();

        Config {
            app_name,
            worker_count,
            lookup,
        }
    }
}

static CONFIG: LazyLock<Config> = LazyLock::new(Config::load);

fn main() {
    println!("app name:     {}", CONFIG.app_name);
    println!("worker count: {}", CONFIG.worker_count);
    println!("lookup for 'g': {:?}", CONFIG.lookup.get("g"));
    println!("same instance: {}", std::ptr::eq(&*CONFIG, &*CONFIG));
}
