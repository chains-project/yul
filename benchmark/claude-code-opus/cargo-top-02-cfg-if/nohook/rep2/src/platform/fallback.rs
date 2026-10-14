//! Fallback for targets without a dedicated backend.

#[must_use]
pub fn family() -> &'static str {
    "unknown"
}

#[must_use]
pub fn path_separator() -> char {
    '/'
}
