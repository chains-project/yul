//! Backend for `target_family = "wasm"`.

use super::Family;

/// Returns the platform family.
pub const fn family() -> Family {
    Family::Wasm
}

/// The character separating path components.
pub const fn path_separator() -> char {
    '/'
}

/// The suffix appended to executable files.
pub const fn exe_suffix() -> &'static str {
    ""
}

/// The suffix used by WebAssembly modules.
pub const fn dylib_suffix() -> &'static str {
    ".wasm"
}

/// The line ending used by the platform.
pub const fn line_ending() -> &'static str {
    "\n"
}
