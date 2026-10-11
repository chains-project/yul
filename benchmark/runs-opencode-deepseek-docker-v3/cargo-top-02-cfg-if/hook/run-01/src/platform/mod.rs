//! Platform implementations.
//!
//! Exactly one of the modules below is compiled, chosen by the alias emitted
//! in `build.rs`. Every implementation exposes the same items, so the rest of
//! the crate can reach them through the `imp` alias without any further
//! `#[cfg]` noise.

#[cfg(platform_unix)]
pub(crate) mod unix;
#[cfg(platform_unix)]
pub(crate) use unix as imp;

#[cfg(platform_windows)]
pub(crate) mod windows;
#[cfg(platform_windows)]
pub(crate) use windows as imp;

#[cfg(platform_wasm)]
pub(crate) mod wasm;
#[cfg(platform_wasm)]
pub(crate) use wasm as imp;

#[cfg(platform_other)]
pub(crate) mod other;
#[cfg(platform_other)]
pub(crate) use other as imp;

/// The operating-system family the crate was built for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Platform {
    /// A member of the `unix` family (Linux, macOS, the BSDs, ...).
    Unix,
    /// A member of the `windows` family.
    Windows,
    /// A member of the `wasm` family, including WASI.
    Wasm,
    /// Any target that is not one of the above.
    Other,
}

impl Platform {
    /// A stable, human-readable name for the platform.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Unix => "unix",
            Self::Windows => "windows",
            Self::Wasm => "wasm",
            Self::Other => "other",
        }
    }
}

impl core::fmt::Display for Platform {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(self.name())
    }
}
