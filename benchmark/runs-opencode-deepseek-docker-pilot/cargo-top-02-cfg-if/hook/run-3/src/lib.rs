//! Small cross-platform helpers.
//!
//! Every target-specific value is selected through a single [`cfg_if!`] block
//! instead of a pile of `#[cfg(...)]` attributes. Adding a new platform is one
//! extra branch, and each branch stays flat and easy to read.

#![forbid(unsafe_code)]

use cfg_if::cfg_if;

/// The platform this build targets.
pub struct Platform {
    /// Short name of the platform family.
    pub name: &'static str,
    /// Separator used between path components.
    pub path_separator: char,
    /// Line ending used by text files on the platform.
    pub line_ending: &'static str,
}

cfg_if! {
    if #[cfg(target_arch = "wasm32")] {
        /// The platform this build targets.
        pub const CURRENT: Platform = Platform {
            name: "wasm32",
            path_separator: '/',
            line_ending: "\n",
        };
    } else if #[cfg(windows)] {
        /// The platform this build targets.
        pub const CURRENT: Platform = Platform {
            name: "windows",
            path_separator: '\\',
            line_ending: "\r\n",
        };
    } else if #[cfg(unix)] {
        /// The platform this build targets.
        pub const CURRENT: Platform = Platform {
            name: "unix",
            path_separator: '/',
            line_ending: "\n",
        };
    } else {
        /// The platform this build targets.
        pub const CURRENT: Platform = Platform {
            name: "unknown",
            path_separator: '/',
            line_ending: "\n",
        };
    }
}

/// Joins `parts` with the target platform's path separator.
pub fn join(parts: &[&str]) -> String {
    parts.join(&CURRENT.path_separator.to_string())
}

/// Normalizes `text` to the target platform's line ending.
pub fn to_native_line_endings(text: &str) -> String {
    let unified = text.replace("\r\n", "\n");
    if CURRENT.line_ending == "\n" {
        unified
    } else {
        unified.replace('\n', CURRENT.line_ending)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn separator_matches_target_family() {
        cfg_if! {
            if #[cfg(windows)] {
                assert_eq!(CURRENT.path_separator, '\\');
            } else {
                assert_eq!(CURRENT.path_separator, '/');
            }
        }
    }

    #[test]
    fn join_uses_platform_separator() {
        assert_eq!(
            join(&["a", "b", "c"]),
            format!("a{}b{}c", CURRENT.path_separator, CURRENT.path_separator)
        );
    }

    #[test]
    fn line_endings_are_normalized_idempotently() {
        let once = to_native_line_endings("a\r\nb\nc");
        assert_eq!(to_native_line_endings(&once), once);
    }
}
