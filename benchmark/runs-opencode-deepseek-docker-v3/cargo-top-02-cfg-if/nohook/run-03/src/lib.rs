//! Small, dependency-light helpers for writing cross-platform libraries.
//!
//! Every target-specific decision is made in exactly one place: the
//! [`platform`] module. Callers use ordinary functions and constants and never
//! have to repeat `#[cfg(any(...))]` conditions of their own.
//!
//! ```no_run
//! use platform_kit::{os, path_separator, Os};
//!
//! println!("running on {:?}", os());
//! assert!(matches!(path_separator(), '/' | '\\'));
//! ```

pub mod platform;

pub use platform::{
    Arch, Os, arch, exe_suffix, line_ending, os, path_list_separator, path_separator,
    shared_library_prefix, shared_library_suffix,
};
