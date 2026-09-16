//! # platform-utils
//!
//! A library providing platform-aware utilities with clean conditional compilation.
//!
//! Uses `cfg-if` macros to define platform-specific behavior in a readable,
//! maintainable way across Linux, macOS, Windows, FreeBSD, and OpenBSD.

cfg_if::cfg_if! {
    if #[cfg(target_os = "linux")] {
        mod linux;
        pub use linux::*;
    } else if #[cfg(target_os = "macos")] {
        mod macos;
        pub use macos::*;
    } else if #[cfg(target_os = "windows")] {
        mod windows;
        pub use windows::*;
    } else if #[cfg(target_os = "freebsd")] {
        mod freebsd;
        pub use freebsd::*;
    } else if #[cfg(target_os = "openbsd")] {
        mod openbsd;
        pub use openbsd::*;
    } else {
        mod unknown;
        pub use unknown::*;
    }
}

/// Returns the name of the current platform.
pub fn platform_name() -> &'static str {
    platform_info().0
}

/// Returns platform-specific metadata as `(name, version_hint)`.
pub fn platform_info() -> (&'static str, &'static str) {
    unimplemented!("implementations exist per-target platform")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_platform_name() {
        let name = platform_name();
        assert!(!name.is_empty(), "platform name should not be empty");
    }
}