use tracing_subscriber::EnvFilter;

fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")))
        .json()
        .init();

    tracing::info!("backend service starting");
    tracing::debug!(port = 8080, "listening for connections");
    tracing::warn!("this is a warning-level example event");
    tracing::error!(error = "example", "this is an error-level example event");
}
