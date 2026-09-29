//! Backend for Windows (`windows_family`).
//!
//! Compiled only when the `windows_family` alias from `build.rs` is set.

use crate::platform::Family;

/// Marker type representing the Windows backend.
#[derive(Debug, Clone, Copy, Default)]
pub struct Backend;

impl Backend {
    /// Backend name.
    pub const NAME: &'static str = "windows";
    /// Operating-system family.
    pub const FAMILY: Family = Family::Windows;
    /// Native line ending.
    pub const NEWLINE: &'static str = "\r\n";
    /// Native path separator.
    pub const PATH_SEPARATOR: char = '\\';
}

/// Operating-system page size, in bytes.
///
/// Provided by the `windows-sys` dependency declared under
/// `[target.'cfg(windows)'.dependencies]` in `Cargo.toml`.
#[must_use]
pub fn page_size() -> usize {
    use windows_sys::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};

    // SAFETY: `GetSystemInfo` only writes into the pointer it is given; a
    // zeroed `SYSTEM_INFO` is a valid destination.
    let mut info: SYSTEM_INFO = unsafe { core::mem::zeroed() };
    unsafe { GetSystemInfo(&mut info) };
    info.dwPageSize as usize
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
    fn separator_is_backslash() {
        assert_eq!(Backend::PATH_SEPARATOR, '\\');
    }
}
