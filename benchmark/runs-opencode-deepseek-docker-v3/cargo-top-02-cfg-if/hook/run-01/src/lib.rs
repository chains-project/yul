//! A small cross-platform library that shows how to keep conditional
//! compilation clean and readable across many targets.
//!
//! # The pattern
//!
//! Platform detection happens **once**, in `build.rs`, which maps the raw
//! `CARGO_CFG_TARGET_*` environment variables onto a single semantic alias:
//!
//! | Alias              | Targets                                |
//! |--------------------|----------------------------------------|
//! | `platform_unix`    | `unix` family (Linux, macOS, BSD, ...) |
//! | `platform_windows` | `windows` family                       |
//! | `platform_wasm`    | `wasm` family (WASI and bare wasm)     |
//! | `platform_other`   | everything else                        |
//!
//! From then on the crate only ever tests those aliases. Each platform has one
//! module that provides the same set of items, selected through the private
//! `imp` alias in the `platform` module. Adding a platform means adding one
//! module and one arm in the build script, not hunting down `#[cfg]`s
//! scattered everywhere.
//!
//! # Example
//!
//! ```
//! use multiplatform::{line_ending, path_separator, Platform};
//!
//! let separator = match multiplatform::PLATFORM {
//!     Platform::Windows => '\\',
//!     _ => '/',
//! };
//! assert_eq!(path_separator(), separator);
//! assert!(!line_ending().is_empty());
//! ```

mod platform;

pub use platform::Platform;
pub use platform::imp::{line_ending, path_separator};

/// The platform this crate was compiled for.
///
/// This is a `const`, so it can be used in constant contexts and is resolved
/// entirely at compile time.
pub const PLATFORM: Platform = platform::imp::PLATFORM;
