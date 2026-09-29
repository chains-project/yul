//! Implementation for `cfg(unix)` targets (Linux, macOS, the BSDs, ...).

/// Character used to separate path components.
pub const PATH_SEPARATOR: char = '/';

/// The platform's native newline sequence.
pub const NEWLINE: &str = "\n";

/// Suffix appended to executable files; empty on Unix.
pub const EXE_SUFFIX: &str = "";

/// Returns the identifier of the calling process.
#[must_use]
pub fn process_id() -> u32 {
    // SAFETY: `getpid` takes no arguments, cannot fail, and has no
    // preconditions.
    unsafe { libc::getpid() as u32 }
}
