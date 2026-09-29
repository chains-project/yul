//! Fallback for targets without a dedicated implementation.

use std::time::Duration;

/// Always `0`: this target has no known monotonic clock.
pub fn uptime_millis() -> u128 {
    0
}

/// No-op: this target has no known way to block a thread.
pub fn sleep(_duration: Duration) {}
