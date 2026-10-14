//! WebAssembly backend.

#[must_use]
pub fn family() -> &'static str {
    "wasm"
}

#[must_use]
pub fn path_separator() -> char {
    '/'
}
