//! Implementation for WebAssembly (`target_arch = "wasm32"`) targets.

/// Character used to separate path components.
pub const PATH_SEPARATOR: char = '/';

/// The platform's native newline sequence.
pub const NEWLINE: &str = "\n";

/// Suffix used for WebAssembly modules.
pub const EXE_SUFFIX: &str = ".wasm";

/// Returns the identifier of the calling process.
///
/// WebAssembly has no notion of an operating-system process, so this always
/// returns `0`.
#[must_use]
pub const fn process_id() -> u32 {
    0
}
