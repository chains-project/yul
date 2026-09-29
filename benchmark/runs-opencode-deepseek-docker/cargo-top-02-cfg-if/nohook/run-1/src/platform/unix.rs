//! Backend for Unix-like systems (`unix_family`).
//!
//! Compiled only when the `unix_family` alias from `build.rs` is set, so this
//! file contains no raw `target_*` checks of its own.

use crate::platform::Family;

/// Marker type representing the Unix backend.
#[derive(Debug, Clone, Copy, Default)]
pub struct Backend;

impl Backend {
    /// Backend name.
    pub const NAME: &'static str = "unix";
    /// Operating-system family.
    pub const FAMILY: Family = Family::Unix;
    /// Native line ending.
    pub const NEWLINE: &'static str = "\n";
    /// Native path separator.
    pub const PATH_SEPARATOR: char = '/';
}

/// Operating-system page size, in bytes.
///
/// Provided by the `libc` dependency declared under
/// `[target.'cfg(unix)'.dependencies]` in `Cargo.toml`.
#[must_use]
pub fn page_size() -> usize {
    // `_SC_PAGESIZE` is always a valid name; on failure fall back to 4096.
    let value = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    if value > 0 {
        value as usize
    } else {
        4096
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn page_size_is_a_power_of_two() {
        let size = page_size();
        assert!(size.is_power_of_two(), "unexpected page size: {size}");
    }

    #[test]
    fn separator_is_forward_slash() {
        assert_eq!(Backend::PATH_SEPARATOR, '/');
    }
}
