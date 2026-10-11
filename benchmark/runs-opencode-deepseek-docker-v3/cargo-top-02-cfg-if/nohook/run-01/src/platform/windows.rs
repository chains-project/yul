//! Backend for `target_family = "windows"`.

use super::Family;

/// Returns the platform family.
pub const fn family() -> Family {
    Family::Windows
}

/// The character separating path components.
pub const fn path_separator() -> char {
    '\\'
}

/// The suffix appended to executable files.
pub const fn exe_suffix() -> &'static str {
    ".exe"
}

/// The suffix used by dynamically linked libraries.
pub const fn dylib_suffix() -> &'static str {
    ".dll"
}

/// The line ending used by the platform.
pub const fn line_ending() -> &'static str {
    "\r\n"
}
