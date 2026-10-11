//! Cross-platform primitives with a single, readable conditional-compilation
//! layer.
//!
//! Rather than sprinkling long `#[cfg(all(target_os = "...", ...))]`
//! attributes across the crate, all platform knowledge is concentrated in the
//! private [`platform`] module. That module uses aliases defined in `build.rs`
//! (`platform_windows`, `platform_apple`, ...) and [`cfg_if`] to select exactly
//! one implementation.
//!
//! ```
//! assert!(matches!(crossplat::path_separator(), '/' | '\\'));
//! println!("running on {}", crossplat::current_platform().name());
//! ```

mod platform;

/// A concrete target operating system or environment.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Platform {
    Linux,
    MacOs,
    Windows,
    FreeBsd,
    Wasm,
    Unknown,
}

impl Platform {
    /// A stable, human-readable name for this platform.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Linux => "linux",
            Self::MacOs => "macos",
            Self::Windows => "windows",
            Self::FreeBsd => "freebsd",
            Self::Wasm => "wasm",
            Self::Unknown => "unknown",
        }
    }
}

/// A coarse grouping of platforms that share conventions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Family {
    Unix,
    Windows,
    Wasm,
    Unknown,
}

impl Family {
    /// A stable, human-readable name for this family.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Unix => "unix",
            Self::Windows => "windows",
            Self::Wasm => "wasm",
            Self::Unknown => "unknown",
        }
    }
}

/// The platform this library was compiled for.
#[must_use]
pub const fn current_platform() -> Platform {
    platform::imp::PLATFORM
}

/// The family this library was compiled for.
#[must_use]
pub const fn current_family() -> Family {
    platform::imp::FAMILY
}

/// The character separating path components (`/` or `\`).
#[must_use]
pub const fn path_separator() -> char {
    platform::imp::PATH_SEPARATOR
}

/// The character separating entries in a path list (`:` or `;`).
#[must_use]
pub const fn path_list_separator() -> char {
    platform::imp::PATH_LIST_SEPARATOR
}

/// The line ending used by the target (`\n` or `\r\n`).
#[must_use]
pub const fn line_ending() -> &'static str {
    platform::imp::LINE_ENDING
}

/// The suffix for native executables (`.exe`, `.wasm`, or empty).
#[must_use]
pub const fn executable_suffix() -> &'static str {
    platform::imp::EXECUTABLE_SUFFIX
}

/// Whether the target is a 64-bit architecture.
#[must_use]
pub const fn is_64_bit() -> bool {
    cfg!(pointer_64)
}

/// Whether the target is Unix-like.
#[must_use]
pub const fn is_unix() -> bool {
    cfg!(unix)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn separators_are_valid() {
        assert!(matches!(path_separator(), '/' | '\\'));
        assert!(matches!(path_list_separator(), ':' | ';'));
        assert!(matches!(line_ending(), "\n" | "\r\n"));
    }

    #[test]
    fn family_is_consistent_with_platform() {
        match current_platform() {
            Platform::Windows => assert_eq!(current_family(), Family::Windows),
            Platform::Wasm => assert_eq!(current_family(), Family::Wasm),
            Platform::Linux | Platform::MacOs | Platform::FreeBsd => {
                assert_eq!(current_family(), Family::Unix);
            }
            Platform::Unknown => {}
        }
    }

    #[test]
    fn platform_matches_the_compilation_target() {
        #[cfg(target_os = "linux")]
        assert_eq!(current_platform(), Platform::Linux);

        #[cfg(target_os = "macos")]
        assert_eq!(current_platform(), Platform::MacOs);

        #[cfg(target_os = "windows")]
        assert_eq!(current_platform(), Platform::Windows);
    }

    #[test]
    fn pointer_width_alias_matches_builtin() {
        assert_eq!(is_64_bit(), cfg!(target_pointer_width = "64"));
        assert_eq!(is_unix(), cfg!(unix));
    }
}
