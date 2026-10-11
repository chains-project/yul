use std::sync::LazyLock;

static CONFIG: LazyLock<String> = LazyLock::new(|| {
    let value = std::env::var("APP_ENV").unwrap_or_else(|_| "development".to_string());
    format!("running in {value}")
});

fn main() {
    println!("{}", *CONFIG);
    println!("{}", *CONFIG);
}
