//! `platkit`: a cross-platform library.
//!
//! # Conditional-compilation conventions
//!
//! * All platform selection goes through [`cfg_select!`], never through
//!   stacks of `#[cfg(...)]` / `#[cfg(not(...))]` attributes. Arms are tried
//!   top to bottom and the first match wins, so the order reads like a
//!   `match` and the `_` arm guarantees exactly one branch is compiled.
//! * Platform-specific code lives only in [`sys`] backends. Each backend
//!   exposes the same items with the same signatures; the rest of the crate
//!   is platform-agnostic and calls `sys::*`.
//! * Small, one-off differences may use `cfg_select!` in expression position
//!   instead of adding a new backend item.

#![no_std]

pub mod sys;

/// Broad operating-system family the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Family {
    /// Linux, macOS, the BSDs, and other Unix-like systems.
    Unix,
    /// Microsoft Windows.
    Windows,
    /// WebAssembly (browser or WASI).
    Wasm,
    /// Anything else; uses the portable fallback backend.
    Other,
}

/// Returns the platform family selected at compile time.
pub const fn family() -> Family {
    sys::FAMILY
}

/// Returns the conventional line ending for the target platform.
pub const fn line_ending() -> &'static str {
    sys::LINE_ENDING
}

/// Returns the separator used between entries of `PATH`-like variables.
pub const fn path_list_separator() -> char {
    sys::PATH_LIST_SEPARATOR
}

/// Returns a short, human-readable name for the target OS.
pub const fn os_name() -> &'static str {
    // Example of expression-position `cfg_select!` for a one-off difference.
    cfg_select! {
        target_os = "linux" => "Linux",
        target_os = "macos" => "macOS",
        target_os = "ios" => "iOS",
        target_os = "android" => "Android",
        target_os = "freebsd" => "FreeBSD",
        windows => "Windows",
        target_os = "wasi" => "WASI",
        target_family = "wasm" => "WebAssembly",
        _ => "unknown",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn family_matches_cfg() {
        let expected = cfg_select! {
            unix => Family::Unix,
            windows => Family::Windows,
            target_family = "wasm" => Family::Wasm,
            _ => Family::Other,
        };
        assert_eq!(family(), expected);
    }

    #[test]
    fn line_ending_is_known() {
        assert!(matches!(line_ending(), "\n" | "\r\n"));
    }

    #[test]
    fn os_name_is_not_empty() {
        assert!(!os_name().is_empty());
    }
}
