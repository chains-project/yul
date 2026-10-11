//! Target selection and the types shared by every backend.
//!
//! The [`cfg_if!`] block is the single place where the crate decides which
//! platform backend to compile. Each backend exposes the same small API, so the
//! rest of the crate never has to care which one was chosen.

use cfg_if::cfg_if;

/// The broad platform family this crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Family {
    /// A Unix-like target (Linux, macOS, the BSDs, ...).
    Unix,
    /// A Windows target.
    Windows,
    /// A WebAssembly target.
    Wasm,
    /// Any target without a dedicated backend.
    Other,
}

cfg_if! {
    if #[cfg(target_family = "windows")] {
        #[path = "windows.rs"]
        mod backend;
    } else if #[cfg(target_family = "unix")] {
        #[path = "unix.rs"]
        mod backend;
    } else if #[cfg(target_family = "wasm")] {
        #[path = "wasm.rs"]
        mod backend;
    } else {
        #[path = "fallback.rs"]
        mod backend;
    }
}

pub use backend::{dylib_suffix, exe_suffix, family, line_ending, path_separator};
