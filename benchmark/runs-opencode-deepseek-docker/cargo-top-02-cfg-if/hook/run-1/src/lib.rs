//! Cross-platform helpers built around clean, readable conditional
//! compilation.
//!
//! Raw platform predicates such as `#[cfg(target_os = "windows")]` become
//! noisy once a crate serves more than one or two targets. This crate keeps
//! that noise out of the implementation:
//!
//! 1. `build.rs` defines short aliases (`macos`, `linux`, `desktop`, `wasm`,
//!    ...) with `cfg_aliases!`, so a use site reads `#[cfg(desktop)]` instead
//!    of repeating long `any(...)` predicates.
//! 2. `cfg_if!` selects whole blocks at compile time when several mutually
//!    exclusive branches are involved, instead of stacking several `#[cfg]`
//!    attributes on one item.
//!
//! The result is that each platform decision lives in exactly one place.
//!
//! # Example
//!
//! ```
//! use crossplat::{platform, Platform};
//!
//! let here = Platform::current();
//! assert_eq!(platform::is_desktop_build(), here.is_desktop());
//! assert!(!here.name().is_empty());
//! ```

pub mod paths;
pub mod platform;

pub use platform::Platform;
