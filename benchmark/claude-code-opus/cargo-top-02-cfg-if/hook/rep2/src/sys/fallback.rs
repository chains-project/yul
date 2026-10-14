//! Portable fallback backend for targets without a dedicated implementation.

use crate::Family;

/// Platform family for this backend.
pub const FAMILY: Family = Family::Other;
/// Conventional line ending.
pub const LINE_ENDING: &str = "\n";
/// Separator between entries in `PATH`-like variables.
pub const PATH_LIST_SEPARATOR: char = ':';
