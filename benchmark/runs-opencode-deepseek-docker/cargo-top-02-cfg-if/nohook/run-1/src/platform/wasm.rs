//! Backend for WebAssembly (`wasm_family`).
//!
//! Compiled only when the `wasm_family` alias from `build.rs` is set.

use crate::platform::Family;

/// Marker type representing the WebAssembly backend.
#[derive(Debug, Clone, Copy, Default)]
pub struct Backend;

impl Backend {
    /// Backend name.
    pub const NAME: &'static str = "wasm";
    /// Operating-system family.
    pub const FAMILY: Family = Family::Wasm;
    /// Line ending used by the platform.
    pub const NEWLINE: &'static str = "\n";
    /// Path separator used by the platform.
    pub const PATH_SEPARATOR: char = '/';
}
