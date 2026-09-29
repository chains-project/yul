//! `xplat` — a small cross-platform library scaffold.
//!
//! # Conditional-compilation strategy
//!
//! Raw target detection is confined to exactly two places:
//!
//! 1. [`build.rs`](../../build.rs) defines *semantic cfg aliases* such as
//!    `unix_family` or `has_threads`.
//! 2. [`platform`] maps those aliases onto concrete backends.
//!
//! Everywhere else, write `#[cfg(unix_family)]` — never
//! `#[cfg(target_os = "linux")]`. This keeps conditional blocks short and
//! readable and turns "which platforms exist?" into a single-file question.
//!
//! ```
//! let info = xplat::platform();
//! assert!(!info.name.is_empty());
//! ```

#![cfg_attr(not(feature = "std"), no_std)]
#![deny(unexpected_cfgs)]
#![warn(missing_docs)]

#[cfg(feature = "std")]
extern crate std;

pub mod platform;

pub use platform::{platform, Family, Platform};

/// The version of this crate, taken from `Cargo.toml` at compile time.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
