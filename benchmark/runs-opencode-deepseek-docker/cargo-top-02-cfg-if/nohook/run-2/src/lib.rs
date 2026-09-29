//! A tiny cross-platform utility crate that demonstrates a clean pattern for
//! conditional compilation.
//!
//! # Why this exists
//!
//! `#[cfg]` attributes are powerful but easy to mismanage. When target checks
//! are sprinkled throughout a codebase they become hard to audit, tend to drift
//! out of sync, and only reveal mistakes on the platform you forgot to compile
//! for.
//!
//! This crate keeps that complexity in exactly one place:
//!
//! * [`sys`] owns the *only* target-dispatch table in the crate. It selects a
//!   single backend module — `linux`, `macos`, `windows`, `wasm`, or a generic
//!   `fallback` — from the target triple.
//! * Every backend implements the same `Platform` trait, so adding a platform
//!   means adding one file and one line to the dispatch table. The compiler
//!   then enforces that the new backend supplies the full interface.
//! * The public API below contains no target dispatch at all. It simply asks
//!   the selected backend for the facts it exposes.
//!
//! A couple of genuinely orthogonal target properties (endianness and pointer
//! width) still use plain `#[cfg]`, but they are small, self-contained
//! constants that cannot drift.

mod sys;

use sys::Platform as _;

/// A coarse grouping of target platforms.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Family {
    /// Unix-like systems, including Linux and macOS.
    Unix,
    /// Microsoft Windows.
    Windows,
    /// WebAssembly targets, both `unknown` and WASI.
    Wasm,
    /// A platform this crate has no dedicated backend for.
    Other,
}

/// The byte order of the target.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Endianness {
    /// Least significant byte first, as on x86 and most ARM targets.
    Little,
    /// Most significant byte first, as on big-endian PowerPC and s390x.
    Big,
}

/// Canonical name of the current target platform.
///
/// For the major platforms this matches [`std::env::consts::OS`]: `"linux"`,
/// `"macos"`, or `"windows"`. WebAssembly targets report `"wasm"`, and any
/// platform without a dedicated backend reports its own `std` name.
pub fn name() -> &'static str {
    sys::Imp::NAME
}

/// The coarse [`Family`] the current target belongs to.
pub fn family() -> Family {
    sys::Imp::FAMILY
}

/// The directory separator used by the platform's native paths.
///
/// `'/'` on Unix and WebAssembly, `'\\'` on Windows.
pub fn path_separator() -> char {
    sys::Imp::PATH_SEPARATOR
}

/// The line ending used by the platform's text conventions.
///
/// `"\n"` on Unix and WebAssembly, `"\r\n"` on Windows.
pub fn line_ending() -> &'static str {
    sys::Imp::LINE_ENDING
}

/// Whether the platform's filesystem treats `Foo` and `foo` as distinct.
pub fn has_case_sensitive_filesystem() -> bool {
    sys::Imp::CASE_SENSITIVE_FS
}

/// Join two path fragments with the platform separator.
///
/// The separator is inserted only when `a` does not already end with it, so
/// `join_paths("a/", "b")` and `join_paths("a", "b")` agree on Unix:
///
/// ```
/// let joined = crossplat::join_paths("src", "lib.rs");
/// assert!(joined.ends_with("lib.rs"));
/// ```
pub fn join_paths(a: &str, b: &str) -> String {
    sys::Imp::join(a, b)
}

/// The native [`Endianness`] of the target.
///
/// This is orthogonal to the operating system, so it is expressed directly in
/// terms of the target rather than through the platform backends.
pub fn endianness() -> Endianness {
    ENDIANNESS
}

/// The native [`Endianness`] of the target, as a constant.
#[cfg(target_endian = "little")]
pub const ENDIANNESS: Endianness = Endianness::Little;

/// The native [`Endianness`] of the target, as a constant.
#[cfg(target_endian = "big")]
pub const ENDIANNESS: Endianness = Endianness::Big;

/// Width, in bits, of a pointer and of `usize` on this target.
#[cfg(target_pointer_width = "16")]
pub const POINTER_WIDTH: u32 = 16;

/// Width, in bits, of a pointer and of `usize` on this target.
#[cfg(target_pointer_width = "32")]
pub const POINTER_WIDTH: u32 = 32;

/// Width, in bits, of a pointer and of `usize` on this target.
#[cfg(target_pointer_width = "64")]
pub const POINTER_WIDTH: u32 = 64;
