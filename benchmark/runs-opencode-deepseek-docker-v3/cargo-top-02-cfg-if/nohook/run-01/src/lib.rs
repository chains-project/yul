//! `crossplat` is a tiny platform abstraction layer.
//!
//! The backend implementation is selected once, at the top of [`platform`],
//! using the [`cfg_if!`] macro from the [`cfg-if`] crate. That keeps the
//! conditional-compilation logic in a single readable block instead of
//! scattering `#[cfg(...)]` attributes across the crate.
//!
//! # Examples
//!
//! ```
//! use crossplat::{exe_suffix, path_separator};
//!
//! let mut exe = String::from("tool");
//! exe.push_str(exe_suffix());
//!
//! let joined = format!("bin{sep}tool", sep = path_separator());
//! # let _ = (exe, joined);
//! ```

pub mod platform;

pub use platform::{Family, dylib_suffix, exe_suffix, family, line_ending, path_separator};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn separators_are_single_chars() {
        assert_eq!(path_separator().len_utf8(), 1);
    }

    #[test]
    fn line_endings_are_never_empty() {
        assert!(!line_ending().is_empty());
    }

    #[test]
    fn family_is_consistent_with_target() {
        #[cfg(target_family = "windows")]
        assert_eq!(family(), Family::Windows);

        #[cfg(all(unix, not(target_family = "wasm")))]
        assert_eq!(family(), Family::Unix);
    }
}
