//! `crossplat` demonstrates how to keep conditional compilation out of your
//! public API.
//!
//! The crate exposes a single, platform-independent surface. Every
//! `#[cfg(...)]` lives in [`platform`], which selects one implementation of the
//! [`Platform`] trait. Callers never need to write a `cfg` of their own.

mod platform;

pub use platform::{Current, Platform};

/// The name of the platform currently being compiled for.
#[must_use]
pub fn name() -> &'static str {
    Current::NAME
}

/// The memory page size, in bytes, of the current platform.
#[must_use]
pub fn page_size() -> usize {
    Current::page_size()
}

/// A sensible upper bound on the number of useful worker threads.
#[must_use]
pub fn max_threads() -> usize {
    Current::max_threads()
}
