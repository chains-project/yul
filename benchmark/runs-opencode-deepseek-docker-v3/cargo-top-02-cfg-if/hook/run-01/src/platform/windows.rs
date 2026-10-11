//! `windows` family implementation.

use super::Platform;

/// The platform this implementation represents.
pub(crate) const PLATFORM: Platform = Platform::Windows;

/// The directory separator used by native paths.
#[must_use]
pub const fn path_separator() -> char {
    '\\'
}

/// The native line ending.
#[must_use]
pub const fn line_ending() -> &'static str {
    "\r\n"
}
