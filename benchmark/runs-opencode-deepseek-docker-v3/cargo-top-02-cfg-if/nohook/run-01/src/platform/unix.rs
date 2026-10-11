//! Backend for `target_family = "unix"`.

use cfg_if::cfg_if;

use super::Family;

/// Returns the platform family.
pub const fn family() -> Family {
    Family::Unix
}

/// The character separating path components.
pub const fn path_separator() -> char {
    '/'
}

/// The suffix appended to executable files.
pub const fn exe_suffix() -> &'static str {
    ""
}

/// The suffix used by dynamically linked libraries.
///
/// Apple platforms use `.dylib`; every other Unix uses `.so`.
pub const fn dylib_suffix() -> &'static str {
    cfg_if! {
        if #[cfg(any(target_os = "macos", target_os = "ios"))] {
            ".dylib"
        } else {
            ".so"
        }
    }
}

/// The line ending used by the platform.
pub const fn line_ending() -> &'static str {
    "\n"
}
