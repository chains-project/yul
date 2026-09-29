//! Readable, compile-time conditional compilation across target platforms.
//!
//! # How the conditionals are organised
//!
//! 1. **Semantic aliases, declared once.** `build.rs` maps the raw
//!    `target_*` predicates onto names such as `platform_unix` and
//!    `pointer_64`. Long, stringly-typed predicates then appear in exactly one
//!    place instead of at every call site, and the alias table doubles as
//!    documentation of the supported targets.
//! 2. **A single dispatch point.** Mutually exclusive implementations live in
//!    [`sys`], which selects exactly one module. Upstream code depends only on
//!    the flat re-exports and never names a concrete platform.
//! 3. **Attributes for items, `cfg_if!` for blocks.** `#[cfg]` guards items,
//!    fields, and match arms. Whole statements, imports, and choice of module
//!    cannot be expressed with an attribute, so those use [`cfg_if!`].
//!
//! [`cfg_if!`]: cfg_if::cfg_if
//!
//! # Example
//!
//! ```
//! use portable::{machine_label, PlatformInfo};
//!
//! println!("{} ({})", PlatformInfo::CURRENT, machine_label());
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs)]

pub mod platform;
mod sys;

pub use platform::{Arch, Family, PlatformInfo};
pub use sys::{sleep, uptime_millis};

/// A short, stable label for the current target, such as `"windows-64"`.
///
/// This is the block-level counterpart to the item-level `#[cfg]` guards in
/// [`platform`]: `cfg_if!` selects a whole arm, and each arm `return`s so no
/// value has to escape the macro's scope.
pub fn machine_label() -> &'static str {
    cfg_if::cfg_if! {
        if #[cfg(all(platform_windows, pointer_64))] {
            return "windows-64";
        } else if #[cfg(all(platform_windows, pointer_32))] {
            return "windows-32";
        } else if #[cfg(all(platform_unix, arch_aarch64))] {
            return "unix-aarch64";
        } else if #[cfg(all(platform_unix, arch_x86_64))] {
            return "unix-x86_64";
        } else if #[cfg(platform_unix)] {
            return "unix";
        } else if #[cfg(platform_wasm)] {
            return "wasm";
        } else {
            return "unknown";
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pointer_width_agrees_with_the_compiler() {
        let expected = (core::mem::size_of::<usize>() * 8) as u8;
        assert_eq!(PlatformInfo::CURRENT.pointer_width, expected);
    }

    #[test]
    fn label_is_specific_on_supported_targets() {
        assert_ne!(machine_label(), "unknown");
    }

    #[test]
    fn current_platform_is_classified() {
        assert_ne!(PlatformInfo::CURRENT.family, Family::Unknown);
    }
}
