//! Windows implementation.

use std::sync::OnceLock;
use std::time::{Duration, Instant};

fn origin() -> &'static Instant {
    static ORIGIN: OnceLock<Instant> = OnceLock::new();
    ORIGIN.get_or_init(Instant::now)
}

/// Milliseconds elapsed on a monotonic clock since the first call.
pub fn uptime_millis() -> u128 {
    origin().elapsed().as_millis()
}

/// Blocks the current thread for the given duration.
pub fn sleep(duration: Duration) {
    std::thread::sleep(duration);
}
