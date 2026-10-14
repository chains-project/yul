//! Cross-platform library skeleton.
//!
//! # Conditional-compilation conventions
//!
//! * **Named aliases** — platform groups such as `apple`, `linux_like` and
//!   `bsd` are defined once in `build.rs`; use them instead of repeating
//!   long `any(target_os = ...)` lists.
//! * **`cfg_if!` for chains** — whenever there are more than two mutually
//!   exclusive branches, use `cfg_if::cfg_if!` so the "else" case is explicit
//!   and no branch can be accidentally left uncovered.
//! * **One backend per file** — platform-specific code lives in `src/sys/`,
//!   and every backend exposes the same items. The public API in this file
//!   stays free of `#[cfg]`.

mod sys;

/// Broad operating-system family of the compilation target.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum OsFamily {
    Linux,
    Apple,
    Bsd,
    OtherUnix,
    Windows,
    Wasm,
    Unknown,
}

/// The native line ending for the target platform.
pub const LINE_ENDING: &str = sys::LINE_ENDING;

/// Returns the OS family this crate was compiled for.
pub fn os_family() -> OsFamily {
    sys::os_family()
}

/// Name of the environment variable conventionally used to locate the
/// user's configuration directory, if the platform has one.
pub fn config_dir_env() -> Option<&'static str> {
    sys::config_dir_env()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn os_family_matches_target() {
        let family = os_family();
        cfg_if::cfg_if! {
            if #[cfg(target_os = "linux")] {
                assert_eq!(family, OsFamily::Linux);
            } else if #[cfg(target_os = "macos")] {
                assert_eq!(family, OsFamily::Apple);
            } else if #[cfg(windows)] {
                assert_eq!(family, OsFamily::Windows);
            } else {
                let _ = family;
            }
        }
    }

    #[test]
    fn line_ending_is_nonempty() {
        assert!(LINE_ENDING.ends_with('\n'));
    }
}
