use tracing::{debug, error, info, warn};
use tracing_subscriber::EnvFilter;

fn main() {
    tracing_subscriber::fmt()
        .json()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")))
        .init();

    info!("backend service starting up");
    debug!(port = 8080, "listening for connections");
    warn!("this is a sample warning");
    error!(error = "example error", "this is a sample error");

    info!("backend service ready");
}
