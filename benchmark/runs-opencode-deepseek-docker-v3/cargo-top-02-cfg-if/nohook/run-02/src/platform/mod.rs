//! The single home for target detection in this crate.
//!
//! `current()` is re-exported from whichever platform module matches the
//! build target, so callers see one stable function regardless of `cfg`.

mod info;

pub use info::{Family, Platform};

#[cfg(target_family = "unix")]
mod unix;
#[cfg(target_family = "unix")]
pub use unix::current;

#[cfg(target_family = "windows")]
mod windows;
#[cfg(target_family = "windows")]
pub use windows::current;

#[cfg(target_family = "wasm")]
mod wasm;
#[cfg(target_family = "wasm")]
pub use wasm::current;

#[cfg(not(any(
    target_family = "unix",
    target_family = "windows",
    target_family = "wasm",
)))]
mod fallback;
#[cfg(not(any(
    target_family = "unix",
    target_family = "windows",
    target_family = "wasm",
)))]
pub use fallback::current;
