//! Platform detection and dispatch.
//!
//! This module is the **only** place that resolves the semantic `cfg` aliases
//! from `build.rs` into concrete code. It uses [`cfg_if`] to keep the
//! if/else chain flat instead of stacking `#[cfg(...)]` attributes.
//!
//! Adding a platform means editing this dispatch and adding a backend file
//! next to it; callers keep using the same API.

cfg_if::cfg_if! {
    if #[cfg(unix_family)] {
        mod unix;
        use unix as backend;
    } else if #[cfg(windows_family)] {
        mod windows;
        use windows as backend;
    } else if #[cfg(wasm_family)] {
        mod wasm;
        use wasm as backend;
    } else {
        mod fallback;
        use fallback as backend;
    }
}

pub use backend::Backend;

/// The operating-system family the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Family {
    /// Unix-like systems (`unix_family`).
    Unix,
    /// Windows (`windows_family`).
    Windows,
    /// WebAssembly (`wasm_family`).
    Wasm,
    /// Anything not covered by a dedicated backend.
    Other,
}

/// Which [`Family`] this build targets.
pub const FAMILY: Family = Backend::FAMILY;

/// The line-ending sequence used by the current platform.
pub const NEWLINE: &str = Backend::NEWLINE;

/// The path separator used by the current platform.
pub const PATH_SEPARATOR: char = Backend::PATH_SEPARATOR;

/// A snapshot of properties of the platform this crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub struct Platform {
    /// Backend name, e.g. `"unix"` or `"windows"`.
    pub name: &'static str,
    /// Coarse operating-system family.
    pub family: Family,
    /// Whether pointers are 64 bits wide (`arch_64`).
    pub is_64_bit: bool,
    /// Whether the target is expected to have threads (`has_threads`).
    pub has_threads: bool,
}

/// Returns a [`Platform`] describing the current compilation target.
///
/// This is a `const fn`, so it can be used to initialise constants.
#[must_use]
pub const fn platform() -> Platform {
    Platform {
        name: Backend::NAME,
        family: Backend::FAMILY,
        is_64_bit: cfg!(arch_64),
        has_threads: cfg!(has_threads),
    }
}

/// Operating-system page size, in bytes.
///
/// Only available on platforms with a dedicated, syscall-backed backend
/// (`has_page_size`); portable targets do not expose this function.
#[cfg(has_page_size)]
pub use backend::page_size;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_is_self_consistent() {
        let info = platform();
        assert!(!info.name.is_empty());
        assert_eq!(info.family, FAMILY);
    }

    #[test]
    fn separator_and_newline_are_sane() {
        assert!(['/', '\\'].contains(&PATH_SEPARATOR));
        assert!(["\n", "\r\n"].contains(&NEWLINE));
    }
}
