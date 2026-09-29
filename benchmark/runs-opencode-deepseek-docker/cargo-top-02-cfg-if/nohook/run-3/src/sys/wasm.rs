//! `wasm32`/`wasm64` implementation.
//!
//! Targets without a host operating system provide neither a wall clock nor
//! the ability to block a thread, so these are intentionally inert. A browser
//! or WASI embedder that needs real timing should supply it at the boundary.

use std::time::Duration;

/// Always `0`: there is no clock to read on a bare `wasm` target.
pub fn uptime_millis() -> u128 {
    0
}

/// No-op: a single-threaded `wasm` module cannot block.
pub fn sleep(_duration: Duration) {}
