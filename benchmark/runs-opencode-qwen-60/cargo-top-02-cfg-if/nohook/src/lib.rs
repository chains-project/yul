//! cfg-if-wrapper
//!
//! A library providing clean, readable conditional-compilation blocks across
//! multiple target platforms.
//!
//! # Design
//!
//! This crate demonstrates how to write well-structured `#[cfg(...)]` blocks
//! for cross-platform support. Key patterns used:
//!
//! - Platform detection via OS (`unix`, `windows`, `wasi`, `android`)
//! - Architecture detection (`target_arch`)
//! - Feature flag composition (`all()`, `any()`)
//! - Doc comments that reflect conditional compilation paths

// ─── Platform Detection ───────────────────────────────────────────────────

#[cfg(target_os = "windows")]
mod platform {
    /// Returns "Windows" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "Windows"
    }

    /// Returns true on Windows.
    pub fn is_windows() -> bool {
        true
    }
}

#[cfg(target_os = "linux")]
mod platform {
    /// Returns "Linux" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "Linux"
    }

    /// Returns true on Linux.
    pub fn is_windows() -> bool {
        false
    }
}

#[cfg(target_os = "macos")]
mod platform {
    /// Returns "macOS" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "macOS"
    }

    /// Returns true on macOS.
    pub fn is_windows() -> bool {
        false
    }
}

#[cfg(target_os = "wasi")]
mod platform {
    /// Returns "WASI" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "WASI"
    }

    /// Returns true on WASI.
    pub fn is_windows() -> bool {
        false
    }
}

#[cfg(target_os = "android")]
mod platform {
    /// Returns "Android" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "Android"
    }

    /// Returns true on Android.
    pub fn is_windows() -> bool {
        false
    }
}

// Fallback for any other target
#[cfg(not(any(
    target_os = "windows",
    target_os = "linux",
    target_os = "macos",
    target_os = "wasi",
    target_os = "android"
)))]
mod platform {
    /// Returns "Unknown" — the current platform identifier.
    pub fn platform_name() -> &'static str {
        "Unknown"
    }

    /// Returns true on Windows.
    pub fn is_windows() -> bool {
        false
    }
}

// ─── Architecture-Specific Code ───────────────────────────────────────────

#[cfg(target_arch = "x86_64")]
mod arch {
    /// Returns the pointer width in bytes on the current architecture.
    pub fn pointer_width() -> u32 {
        64
    }

    /// Returns the native endianness: "little" for x86_64.
    pub fn endianness() -> &'static str {
        "little"
    }
}

#[cfg(target_arch = "aarch64")]
mod arch {
    /// Returns the pointer width in bytes on the current architecture.
    pub fn pointer_width() -> u32 {
        64
    }

    /// Returns the native endianness: "little" for aarch64.
    pub fn endianness() -> &'static str {
        "little"
    }
}

#[cfg(target_arch = "x86")]
mod arch {
    /// Returns the pointer width in bytes on the current architecture.
    pub fn pointer_width() -> u32 {
        32
    }

    /// Returns the native endianness: "little" for x86.
    pub fn endianness() -> &'static str {
        "little"
    }
}

#[cfg(target_arch = "arm")]
mod arch {
    /// Returns the pointer width in bytes on the current architecture.
    pub fn pointer_width() -> u32 {
        32
    }

    /// Returns the native endianness: "little" for arm.
    pub fn endianness() -> &'static str {
        "little"
    }
}

// ─── Public API ──────────────────────────────────────────────────────────

/// Returns the name of the current platform.
///
/// # Examples
///
/// ```
/// use cfg_if_wrapper;
/// let name = cfg_if_wrapper::platform_name();
/// assert!(!name.is_empty());
/// ```
pub fn platform_name() -> &'static str {
    platform::platform_name()
}

/// Returns whether the current platform is Windows.
pub fn is_windows() -> bool {
    platform::is_windows()
}

/// Returns the pointer width in bytes for the current architecture.
///
/// # Examples
///
/// ```
/// use cfg_if_wrapper;
/// let bits = cfg_if_wrapper::pointer_width();
/// assert!(bits == 32 || bits == 64);
/// ```
pub fn pointer_width() -> u32 {
    arch::pointer_width()
}

/// Returns the native endianness: `"little"` or `"big"`.
///
/// # Examples
///
/// ```
/// use cfg_if_wrapper;
/// let endian = cfg_if_wrapper::endianness();
/// assert_eq!(endian, "little");
/// ```
pub fn endianness() -> &'static str {
    arch::endianness()
}

/// Returns a formatted string with the platform and architecture info.
///
/// # Examples
///
/// ```
/// use cfg_if_wrapper;
/// let info = cfg_if_wrapper::target_info();
/// assert!(info.contains(cfg_if_wrapper::platform_name()));
/// ```
pub fn target_info() -> String {
    format!(
        "{} {} ({}bit, {} endian)",
        platform::platform_name(),
        cfg_if_wrapper::target_arch(),
        arch::pointer_width(),
        arch::endianness()
    )
}

/// Returns the target architecture string.
///
/// This is a helper to demonstrate `target_arch` as a string value, which
/// is useful in doc comments and runtime output.
pub fn target_arch() -> &'static str {
    // On stable Rust, target_arch is only usable in #[cfg()].
    // We use cfg blocks to map to string literals.
    #[cfg(target_arch = "x86_64")]
    {
        return "x86_64";
    }
    #[cfg(target_arch = "aarch64")]
    {
        return "aarch64";
    }
    #[cfg(target_arch = "x86")]
    {
        return "x86";
    }
    #[cfg(target_arch = "arm")]
    {
        return "arm";
    }
    #[cfg(target_arch = "riscv64")]
    {
        return "riscv64";
    }
    #[cfg(target_arch = "wasm32")]
    {
        return "wasm32";
    }
    #[cfg(target_arch = "powerpc64")]
    {
        return "powerpc64";
    }
    #[cfg(target_arch = "s390x")]
    {
        return "s390x";
    }
    #[cfg(not(any(
        target_arch = "x86_64",
        target_arch = "aarch64",
        target_arch = "x86",
        target_arch = "arm",
        target_arch = "riscv64",
        target_arch = "wasm32",
        target_arch = "powerpc64",
        target_arch = "s390x"
    )))]
    {
        return "unknown";
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_not_empty() {
        assert!(!platform_name().is_empty());
    }

    #[test]
    fn target_info_contains_platform() {
        let info = target_info();
        assert!(info.contains(platform_name()));
    }

    #[test]
    fn pointer_width_is_valid() {
        let bits = pointer_width();
        assert!(bits == 32 || bits == 64);
    }

    #[test]
    fn endianness_is_valid() {
        let endian = endianness();
        assert!(endian == "little" || endian == "big");
    }

    #[test]
    fn is_windows_matches_platform() {
        if is_windows() {
            assert_eq!(platform_name(), "Windows");
        } else {
            assert_ne!(platform_name(), "Windows");
        }
    }
}