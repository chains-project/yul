//! Target detection and per-target behaviour.
//!
//! The implementation module for the current target is selected once, here,
//! with a single [`cfg_if!`](cfg_if::cfg_if) block. The rest of the crate then
//! programs against a small, stable contract (`PATH_SEPARATOR`, `EXE_SUFFIX`,
//! ...), which keeps target-specific code out of the public API.

use cfg_if::cfg_if;

/// Operating system family the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Os {
    /// Microsoft Windows or a Windows-targeted environment.
    Windows,
    /// Apple macOS.
    MacOs,
    /// Linux (GNU or musl).
    Linux,
    /// FreeBSD or another BSD.
    FreeBsd,
    /// Google Android.
    Android,
    /// Apple iOS.
    Ios,
    /// WebAssembly (`wasm32`).
    Wasm,
    /// Any target not recognised above.
    Other,
}

/// CPU architecture family the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Arch {
    /// 32-bit x86.
    X86,
    /// 64-bit x86.
    X86_64,
    /// 32-bit ARM.
    Arm,
    /// 64-bit ARM.
    Aarch64,
    /// RISC-V.
    Riscv,
    /// WebAssembly (`wasm32`).
    Wasm32,
    /// Any architecture not recognised above.
    Other,
}

cfg_if! {
    if #[cfg(target_arch = "wasm32")] {
        pub(crate) mod wasm;
        pub(crate) use self::wasm as imp;
    } else if #[cfg(windows)] {
        pub(crate) mod windows;
        pub(crate) use self::windows as imp;
    } else if #[cfg(unix)] {
        pub(crate) mod unix;
        pub(crate) use self::unix as imp;
    } else {
        pub(crate) mod fallback;
        pub(crate) use self::fallback as imp;
    }
}

cfg_if! {
    if #[cfg(target_os = "windows")] {
        const DETECTED_OS: Os = Os::Windows;
    } else if #[cfg(target_os = "macos")] {
        const DETECTED_OS: Os = Os::MacOs;
    } else if #[cfg(target_os = "linux")] {
        const DETECTED_OS: Os = Os::Linux;
    } else if #[cfg(target_os = "freebsd")] {
        const DETECTED_OS: Os = Os::FreeBsd;
    } else if #[cfg(target_os = "android")] {
        const DETECTED_OS: Os = Os::Android;
    } else if #[cfg(target_os = "ios")] {
        const DETECTED_OS: Os = Os::Ios;
    } else if #[cfg(target_arch = "wasm32")] {
        const DETECTED_OS: Os = Os::Wasm;
    } else {
        const DETECTED_OS: Os = Os::Other;
    }
}

cfg_if! {
    if #[cfg(target_arch = "x86")] {
        const DETECTED_ARCH: Arch = Arch::X86;
    } else if #[cfg(target_arch = "x86_64")] {
        const DETECTED_ARCH: Arch = Arch::X86_64;
    } else if #[cfg(target_arch = "arm")] {
        const DETECTED_ARCH: Arch = Arch::Arm;
    } else if #[cfg(target_arch = "aarch64")] {
        const DETECTED_ARCH: Arch = Arch::Aarch64;
    } else if #[cfg(any(target_arch = "riscv32", target_arch = "riscv64"))] {
        const DETECTED_ARCH: Arch = Arch::Riscv;
    } else if #[cfg(target_arch = "wasm32")] {
        const DETECTED_ARCH: Arch = Arch::Wasm32;
    } else {
        const DETECTED_ARCH: Arch = Arch::Other;
    }
}

impl Os {
    /// Returns `true` when this is a Windows-family target.
    pub const fn is_windows(self) -> bool {
        matches!(self, Os::Windows)
    }

    /// Returns `true` when this is a Unix-family target.
    pub const fn is_unix(self) -> bool {
        matches!(
            self,
            Os::MacOs | Os::Linux | Os::FreeBsd | Os::Android | Os::Ios
        )
    }
}

/// Returns the operating system the crate was compiled for.
pub const fn os() -> Os {
    DETECTED_OS
}

/// Returns the CPU architecture the crate was compiled for.
pub const fn arch() -> Arch {
    DETECTED_ARCH
}

/// Returns the character used to separate components of a path.
pub const fn path_separator() -> char {
    imp::PATH_SEPARATOR
}

/// Returns the character used to separate entries in a path list (`PATH`).
pub const fn path_list_separator() -> char {
    imp::PATH_LIST_SEPARATOR
}

/// Returns the executable suffix, including the leading dot when present.
pub const fn exe_suffix() -> &'static str {
    imp::EXE_SUFFIX
}

/// Returns the prefix used by shared libraries on this target.
pub const fn shared_library_prefix() -> &'static str {
    imp::SHARED_LIBRARY_PREFIX
}

/// Returns the suffix used by shared libraries on this target.
pub const fn shared_library_suffix() -> &'static str {
    imp::SHARED_LIBRARY_SUFFIX
}

/// Returns the conventional line ending for text files on this target.
pub const fn line_ending() -> &'static str {
    imp::LINE_ENDING
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detected_targets_are_consistent() {
        assert!(!os().is_windows() || !os().is_unix());
        if cfg!(unix) {
            assert!(os().is_unix(), "expected a Unix Os on a unix target");
        }
        if cfg!(windows) {
            assert!(
                os().is_windows(),
                "expected a Windows Os on a windows target"
            );
        }
    }

    #[test]
    fn behaviour_is_self_consistent() {
        assert!(matches!(path_separator(), '/' | '\\'));
        assert!(matches!(path_list_separator(), ':' | ';'));
        assert!(shared_library_suffix().starts_with('.'));
    }
}
