//! `wasm` family implementation, including WASI.

use super::Platform;

/// The platform this implementation represents.
pub(crate) const PLATFORM: Platform = Platform::Wasm;

/// The directory separator used by native paths.
#[must_use]
pub const fn path_separator() -> char {
    '/'
}

/// The native line ending.
#[must_use]
pub const fn line_ending() -> &'static str {
    "\n"
}
