//! Unix backend (Linux, macOS, BSDs, ...).

#[must_use]
pub fn family() -> &'static str {
    "unix"
}

#[must_use]
pub fn path_separator() -> char {
    '/'
}
