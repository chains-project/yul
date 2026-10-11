//! Backend for targets without a dedicated implementation.

use super::Family;

/// Returns the platform family.
pub const fn family() -> Family {
    Family::Other
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
pub const fn dylib_suffix() -> &'static str {
    ""
}

/// The line ending used by the platform.
pub const fn line_ending() -> &'static str {
    "\n"
}
