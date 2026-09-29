use std::sync::LazyLock;

#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
    allowed_users: Vec<String>,
}

impl Config {
    fn from_env() -> Self {
        let host = std::env::var("APP_HOST").unwrap_or_else(|_| "127.0.0.1".to_owned());

        let port = std::env::var("APP_PORT")
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or(8080);

        let allowed_users = std::env::var("APP_USERS")
            .map(|users| {
                users
                    .split(',')
                    .map(str::trim)
                    .filter(|user| !user.is_empty())
                    .map(str::to_owned)
                    .collect()
            })
            .unwrap_or_default();

        Self {
            host,
            port,
            allowed_users,
        }
    }
}

static CONFIG: LazyLock<Config> = LazyLock::new(Config::from_env);

fn main() {
    println!("listening on {}:{}", CONFIG.host, CONFIG.port);
    println!("allowed users: {:?}", CONFIG.allowed_users);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn config_is_initialized_once() {
        let first: &'static Config = &CONFIG;
        let second: &'static Config = &CONFIG;
        assert!(std::ptr::eq(first, second));
    }
}
