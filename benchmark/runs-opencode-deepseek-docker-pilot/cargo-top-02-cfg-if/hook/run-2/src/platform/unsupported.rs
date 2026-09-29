//! Fallback implementation for targets without a dedicated module.
//!
//! Keeping this branch lets the crate compile for any target, and it makes the
//! [`cfg_if!`](https://docs.rs/cfg-if) chain exhaustive instead of silently
//! producing a confusing "unresolved import" error.

/// Character used to separate path components.
pub const PATH_SEPARATOR: char = '/';

/// The platform's native newline sequence.
pub const NEWLINE: &str = "\n";

/// Suffix appended to executable files.
pub const EXE_SUFFIX: &str = "";

/// Returns the identifier of the calling process.
///
/// This target has no known process API, so this always returns `0`.
#[must_use]
pub const fn process_id() -> u32 {
    0
}
