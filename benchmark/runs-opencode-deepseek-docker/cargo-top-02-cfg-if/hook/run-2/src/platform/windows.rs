//! Implementation for `cfg(windows)` targets.

/// Character used to separate path components.
pub const PATH_SEPARATOR: char = '\\';

/// The platform's native newline sequence.
pub const NEWLINE: &str = "\r\n";

/// Suffix appended to executable files.
pub const EXE_SUFFIX: &str = ".exe";

/// Returns the identifier of the calling process.
#[must_use]
pub fn process_id() -> u32 {
    // SAFETY: `GetCurrentProcessId` takes no arguments, cannot fail, and has
    // no preconditions.
    unsafe { windows_sys::Win32::System::Threading::GetCurrentProcessId() }
}
