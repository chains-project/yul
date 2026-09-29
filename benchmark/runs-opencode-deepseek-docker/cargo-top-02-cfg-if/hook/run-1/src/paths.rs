//! Per-platform path conventions.
//!
//! This module demonstrates a *behavioural* platform split: the same public
//! function has a different body on each target, selected with `cfg_if!`.

use cfg_if::cfg_if;

/// Returns the separator between path components on this platform.
#[must_use]
pub const fn separator() -> char {
    cfg_if! {
        if #[cfg(windows)] {
            '\\'
        } else {
            '/'
        }
    }
}

/// Returns the separator between entries of a `PATH`-like environment
/// variable on this platform.
#[must_use]
pub const fn env_separator() -> char {
    cfg_if! {
        if #[cfg(windows)] {
            ';'
        } else {
            ':'
        }
    }
}

/// Returns the conventional extension for a dynamically linked library,
/// without a leading dot.
#[must_use]
pub const fn dynamic_library_extension() -> &'static str {
    cfg_if! {
        if #[cfg(windows)] {
            "dll"
        } else if #[cfg(macos)] {
            "dylib"
        } else if #[cfg(linux)] {
            "so"
        } else {
            "bin"
        }
    }
}

#[cfg(test)]
mod tests {
    #[cfg(any(windows, macos, linux))]
    use super::{dynamic_library_extension, env_separator, separator};

    #[cfg(windows)]
    #[test]
    fn windows_conventions() {
        assert_eq!(separator(), '\\');
        assert_eq!(env_separator(), ';');
        assert_eq!(dynamic_library_extension(), "dll");
    }

    #[cfg(macos)]
    #[test]
    fn macos_conventions() {
        assert_eq!(separator(), '/');
        assert_eq!(env_separator(), ':');
        assert_eq!(dynamic_library_extension(), "dylib");
    }

    #[cfg(linux)]
    #[test]
    fn linux_conventions() {
        assert_eq!(separator(), '/');
        assert_eq!(env_separator(), ':');
        assert_eq!(dynamic_library_extension(), "so");
    }
}
