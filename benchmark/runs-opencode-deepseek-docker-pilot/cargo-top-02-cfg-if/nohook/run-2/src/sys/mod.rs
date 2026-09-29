//! Platform backends.
//!
//! This is the *only* module in the crate that performs target dispatch. The
//! [`Platform`] trait defines the interface a backend must provide, and the
//! `imp` module alias below selects exactly one backend file for the target
//! being compiled.
//!
//! Adding a platform is a two-step change: drop a new file into this directory
//! and add a single `cfg_attr` line to the mapping table. The compiler will
//! reject the build if the new backend is missing part of the interface.

use crate::Family;

/// The interface every platform backend implements.
///
/// Keeping this in one trait means the target-specific details are guaranteed
/// to line up across platforms, and the public API never has to branch on the
/// target itself.
pub(crate) trait Platform {
    /// Canonical target name, e.g. `"linux"`.
    const NAME: &'static str;

    /// Coarse grouping this target belongs to.
    const FAMILY: Family;

    /// Native directory separator.
    const PATH_SEPARATOR: char;

    /// Native line ending.
    const LINE_ENDING: &'static str;

    /// Whether the native filesystem is case sensitive.
    const CASE_SENSITIVE_FS: bool;

    /// Join two path fragments, inserting [`Self::PATH_SEPARATOR`] when needed.
    fn join(a: &str, b: &str) -> String {
        let mut out = String::with_capacity(a.len() + b.len() + 1);
        out.push_str(a);
        if !a.ends_with(Self::PATH_SEPARATOR) {
            out.push(Self::PATH_SEPARATOR);
        }
        out.push_str(b);
        out
    }
}

// Exactly one arm below matches any given target, so `path` is never set twice.
#[cfg_attr(target_os = "linux", path = "linux.rs")]
#[cfg_attr(target_os = "macos", path = "macos.rs")]
#[cfg_attr(target_os = "windows", path = "windows.rs")]
#[cfg_attr(target_arch = "wasm32", path = "wasm.rs")]
#[cfg_attr(
    not(any(
        target_os = "linux",
        target_os = "macos",
        target_os = "windows",
        target_arch = "wasm32",
    )),
    path = "fallback.rs"
)]
pub(crate) mod imp;

pub(crate) use imp::Imp;
