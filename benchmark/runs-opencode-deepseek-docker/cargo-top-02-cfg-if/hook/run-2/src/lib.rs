#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(docsrs, feature(doc_cfg))]
#![warn(missing_docs)]

//! # `xplat`
//!
//! A tiny library that shows how to keep conditional compilation clean and
//! readable when code has to serve many target platforms.
//!
//! ## The pattern
//!
//! All target detection is concentrated in the [`platform`] module. Callers
//! depend on a single, target-independent API instead of sprinkling `#[cfg]`
//! attributes throughout the crate:
//!
//! ```
//! let platform = xplat::Platform::current();
//! println!("running on {platform}");
//! ```
//!
//! Three mechanisms work together:
//!
//! * [`cfg_if!`](https://docs.rs/cfg-if) for readable `if` / `else if` chains
//!   instead of stacking mutually exclusive `#[cfg]` attributes on every item.
//! * `[target.'cfg(...)'.dependencies]` in `Cargo.toml` so OS-specific crates
//!   such as `libc` are only compiled for the OS that needs them.
//! * A `std` feature for capability gating that is orthogonal to the target.

pub mod platform;

pub use platform::{EXE_SUFFIX, NEWLINE, PATH_SEPARATOR, Platform, process_id};

/// Returns the path of the currently running executable.
///
/// This is only available when the `std` feature is enabled, because it relies
/// on [`std::env`].
#[cfg(feature = "std")]
#[cfg_attr(docsrs, doc(cfg(feature = "std")))]
pub fn current_exe() -> std::io::Result<std::path::PathBuf> {
    std::env::current_exe()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reports_a_platform_name() {
        assert!(!Platform::current().name().is_empty());
    }

    #[test]
    fn newline_matches_the_platform() {
        if cfg!(windows) {
            assert_eq!(NEWLINE, "\r\n");
        } else {
            assert_eq!(NEWLINE, "\n");
        }
    }

    #[test]
    fn process_id_is_nonzero_on_native_targets() {
        if !cfg!(target_arch = "wasm32") {
            assert_ne!(process_id(), 0);
        }
    }

    #[cfg(feature = "std")]
    #[test]
    fn current_exe_resolves() {
        assert!(current_exe().is_ok());
    }
}
