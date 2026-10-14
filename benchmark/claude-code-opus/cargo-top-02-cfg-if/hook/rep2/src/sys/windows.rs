//! Windows backend.

use crate::Family;

/// Platform family for this backend.
pub const FAMILY: Family = Family::Windows;
/// Conventional line ending.
pub const LINE_ENDING: &str = "\r\n";
/// Separator between entries in `PATH`-like variables.
pub const PATH_LIST_SEPARATOR: char = ';';
