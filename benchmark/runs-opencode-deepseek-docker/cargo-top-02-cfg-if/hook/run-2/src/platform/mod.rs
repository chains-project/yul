//! Target detection and OS-specific primitives.
//!
//! Every `#[cfg]` decision lives behind this module so the rest of the crate
//! can stay target-agnostic. The dispatch below uses [`cfg_if!`] instead of a
//! stack of mutually exclusive `#[cfg]` attributes, which keeps the mapping
//! from target to implementation readable in one place.
//!
//! [`cfg_if!`]: https://docs.rs/cfg-if

use core::fmt;

cfg_if::cfg_if! {
    if #[cfg(target_arch = "wasm32")] {
        mod wasm;
        pub use wasm::{EXE_SUFFIX, NEWLINE, PATH_SEPARATOR, process_id};
    } else if #[cfg(unix)] {
        mod unix;
        pub use unix::{EXE_SUFFIX, NEWLINE, PATH_SEPARATOR, process_id};
    } else if #[cfg(windows)] {
        mod windows;
        pub use windows::{EXE_SUFFIX, NEWLINE, PATH_SEPARATOR, process_id};
    } else {
        mod unsupported;
        pub use unsupported::{EXE_SUFFIX, NEWLINE, PATH_SEPARATOR, process_id};
    }
}

/// The operating-system family this crate was compiled for.
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
#[non_exhaustive]
pub enum Platform {
    /// Linux.
    Linux,
    /// macOS.
    MacOs,
    /// Windows.
    Windows,
    /// FreeBSD.
    FreeBsd,
    /// Android.
    Android,
    /// iOS.
    Ios,
    /// WebAssembly (`target_arch = "wasm32"`).
    Wasm,
    /// Any other target, carrying its `target_os` value.
    Other(&'static str),
}

impl Platform {
    /// Returns the [`Platform`] for the current compilation target.
    #[must_use]
    pub const fn current() -> Self {
        cfg_if::cfg_if! {
            if #[cfg(target_arch = "wasm32")] {
                Self::Wasm
            } else if #[cfg(target_os = "linux")] {
                Self::Linux
            } else if #[cfg(target_os = "macos")] {
                Self::MacOs
            } else if #[cfg(windows)] {
                Self::Windows
            } else if #[cfg(target_os = "freebsd")] {
                Self::FreeBsd
            } else if #[cfg(target_os = "android")] {
                Self::Android
            } else if #[cfg(target_os = "ios")] {
                Self::Ios
            } else {
                Self::Other(core::env::consts::OS)
            }
        }
    }

    /// Returns a lowercase, machine-friendly name such as `"linux"`.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Linux => "linux",
            Self::MacOs => "macos",
            Self::Windows => "windows",
            Self::FreeBsd => "freebsd",
            Self::Android => "android",
            Self::Ios => "ios",
            Self::Wasm => "wasm",
            Self::Other(name) => name,
        }
    }
}

impl fmt::Display for Platform {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.name())
    }
}
