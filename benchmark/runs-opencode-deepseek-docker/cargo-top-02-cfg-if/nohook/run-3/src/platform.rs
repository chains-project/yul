//! Compile-time information about the target platform.
//!
//! Every value in this module is resolved by the compiler; no runtime probing
//! is involved. The [`Family`] and [`Arch`] values are derived from the
//! aliases declared in `build.rs`, so adding a target means updating one table
//! instead of chasing stringly-typed predicates through the codebase.

use core::fmt;

/// Broad operating-system family the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum Family {
    /// Windows (any edition, any toolchain).
    Windows,
    /// Unix-like systems: Linux, macOS, the BSDs, Solaris, ...
    Unix,
    /// `wasm32`/`wasm64` targets without a host operating system.
    Wasm,
    /// A target this crate has no dedicated support for.
    Unknown,
}

/// CPU architecture the crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum Arch {
    /// 32-bit x86.
    X86,
    /// 64-bit x86 (including `x86_64` and `amd64`).
    X86_64,
    /// 64-bit ARM.
    Aarch64,
    /// Any other architecture.
    Other,
}

/// A snapshot of the target selected when the crate was compiled.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PlatformInfo {
    /// Operating-system family.
    pub family: Family,
    /// CPU architecture.
    pub arch: Arch,
    /// Width of a pointer in bits, or `0` if it is neither 32 nor 64.
    pub pointer_width: u8,
}

// Exactly one of these applies; the guards mirror the `build.rs` alias table.
#[cfg(platform_windows)]
const FAMILY: Family = Family::Windows;
#[cfg(platform_unix)]
const FAMILY: Family = Family::Unix;
#[cfg(platform_wasm)]
const FAMILY: Family = Family::Wasm;
#[cfg(not(any(platform_windows, platform_unix, platform_wasm)))]
const FAMILY: Family = Family::Unknown;

#[cfg(arch_x86)]
const ARCH: Arch = Arch::X86;
#[cfg(arch_x86_64)]
const ARCH: Arch = Arch::X86_64;
#[cfg(arch_aarch64)]
const ARCH: Arch = Arch::Aarch64;
#[cfg(not(any(arch_x86, arch_x86_64, arch_aarch64)))]
const ARCH: Arch = Arch::Other;

#[cfg(pointer_64)]
const POINTER_WIDTH: u8 = 64;
#[cfg(pointer_32)]
const POINTER_WIDTH: u8 = 32;
#[cfg(not(any(pointer_64, pointer_32)))]
const POINTER_WIDTH: u8 = 0;

impl PlatformInfo {
    /// The platform this crate was compiled for.
    pub const CURRENT: Self = Self {
        family: FAMILY,
        arch: ARCH,
        pointer_width: POINTER_WIDTH,
    };

    /// `true` for the operating systems most desktop applications target.
    pub const fn is_desktop(self) -> bool {
        matches!(self.family, Family::Windows | Family::Unix)
    }

    /// `true` when pointers are 64 bits wide.
    pub const fn is_64_bit(self) -> bool {
        self.pointer_width == 64
    }
}

impl fmt::Display for Family {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Family::Windows => "windows",
            Family::Unix => "unix",
            Family::Wasm => "wasm",
            Family::Unknown => "unknown",
        };
        f.write_str(name)
    }
}

impl fmt::Display for Arch {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Arch::X86 => "x86",
            Arch::X86_64 => "x86_64",
            Arch::Aarch64 => "aarch64",
            Arch::Other => "other",
        };
        f.write_str(name)
    }
}

impl fmt::Display for PlatformInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}-{}-{}bit", self.family, self.arch, self.pointer_width)
    }
}
