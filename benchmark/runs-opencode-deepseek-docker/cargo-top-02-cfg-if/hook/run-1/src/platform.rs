//! Compile-time platform detection.
//!
//! Every predicate used here comes from a `cfg` alias declared in `build.rs`,
//! which keeps the branches short and self-documenting.

use cfg_if::cfg_if;

/// The coarse-grained platform a build targets.
///
/// The granularity is intentional: dependent code usually cares whether it is
/// on Windows, a Unix, mobile, or the web, not about the exact OS version.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Platform {
    /// Microsoft Windows.
    Windows,
    /// Apple macOS.
    MacOs,
    /// Linux.
    Linux,
    /// Google Android.
    Android,
    /// Apple iOS.
    Ios,
    /// A 32-bit WebAssembly target.
    Wasm,
    /// Any target this crate does not special-case.
    Other,
}

impl Platform {
    /// Returns the platform this crate was compiled for.
    ///
    /// The branch is selected at compile time, so the result is a constant.
    #[must_use]
    pub const fn current() -> Self {
        cfg_if! {
            if #[cfg(windows)] {
                Self::Windows
            } else if #[cfg(macos)] {
                Self::MacOs
            } else if #[cfg(linux)] {
                Self::Linux
            } else if #[cfg(android)] {
                Self::Android
            } else if #[cfg(ios)] {
                Self::Ios
            } else if #[cfg(wasm)] {
                Self::Wasm
            } else {
                Self::Other
            }
        }
    }

    /// Returns the lowercase, stable name of the platform.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Windows => "windows",
            Self::MacOs => "macos",
            Self::Linux => "linux",
            Self::Android => "android",
            Self::Ios => "ios",
            Self::Wasm => "wasm",
            Self::Other => "other",
        }
    }

    /// Returns `true` for platforms with a windowing desktop environment.
    #[must_use]
    pub const fn is_desktop(self) -> bool {
        matches!(self, Self::Windows | Self::MacOs | Self::Linux)
    }

    /// Returns `true` for mobile operating systems.
    #[must_use]
    pub const fn is_mobile(self) -> bool {
        matches!(self, Self::Android | Self::Ios)
    }
}

/// Returns `true` when compiled for a desktop platform.
///
/// This uses the `desktop` alias directly because a single boolean is all the
/// caller needs.
#[must_use]
pub const fn is_desktop_build() -> bool {
    cfg!(desktop)
}

/// Returns `true` when compiled for a mobile platform.
#[must_use]
pub const fn is_mobile_build() -> bool {
    cfg!(mobile)
}

/// Returns `true` when the target supports threads.
#[must_use]
pub const fn has_threads() -> bool {
    cfg!(has_threads)
}

/// Returns the pointer width of the target in bits.
///
/// Returns `0` for the rare target whose width is neither 32 nor 64 bits.
#[must_use]
pub const fn pointer_width() -> u32 {
    cfg_if! {
        if #[cfg(ptr_64)] {
            64
        } else if #[cfg(ptr_32)] {
            32
        } else {
            0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detection_matches_the_alias_groupings() {
        assert_eq!(is_desktop_build(), Platform::current().is_desktop());
        assert_eq!(is_mobile_build(), Platform::current().is_mobile());
    }

    #[test]
    fn pointer_width_matches_the_standard_library() {
        assert_eq!(pointer_width(), usize::BITS);
    }

    #[test]
    fn name_is_never_empty() {
        assert!(!Platform::current().name().is_empty());
    }
}
