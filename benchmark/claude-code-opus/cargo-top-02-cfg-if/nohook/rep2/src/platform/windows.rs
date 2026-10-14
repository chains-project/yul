//! Windows backend.

#[must_use]
pub fn family() -> &'static str {
    "windows"
}

#[must_use]
pub fn path_separator() -> char {
    '\\'
}
