//! Portable fallback backend.
//!
//! Compiled for any target that is not Unix, Windows or WebAssembly. It makes
//! no operating-system assumptions, which keeps the crate buildable for new or
//! exotic targets without touching the rest of the code.

use crate::platform::Family;

/// Marker type representing the portable fallback backend.
#[derive(Debug, Clone, Copy, Default)]
pub struct Backend;

impl Backend {
    /// Backend name.
    pub const NAME: &'static str = "fallback";
    /// Operating-system family.
    pub const FAMILY: Family = Family::Other;
    /// Line ending used by the platform.
    pub const NEWLINE: &'static str = "\n";
    /// Path separator used by the platform.
    pub const PATH_SEPARATOR: char = '/';
}
