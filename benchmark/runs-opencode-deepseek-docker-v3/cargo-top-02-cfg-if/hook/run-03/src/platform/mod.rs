//! Compile-time platform selection.
//!
//! `build.rs` rewrites target predicates into short aliases
//! (`platform_windows`, `platform_apple`, ...). This module compiles exactly
//! one implementation and re-exports it as `imp`, so the rest of the crate
//! only ever talks to `platform::imp` with no `#[cfg]` noise.

#[cfg(unix)]
pub(crate) mod unix_common;

cfg_if::cfg_if! {
    if #[cfg(platform_windows)] {
        pub(crate) mod windows;
        pub(crate) use self::windows as imp;
    } else if #[cfg(platform_apple)] {
        pub(crate) mod apple;
        pub(crate) use self::apple as imp;
    } else if #[cfg(platform_linux)] {
        pub(crate) mod linux;
        pub(crate) use self::linux as imp;
    } else if #[cfg(platform_bsd)] {
        pub(crate) mod bsd;
        pub(crate) use self::bsd as imp;
    } else if #[cfg(platform_wasm)] {
        pub(crate) mod wasm;
        pub(crate) use self::wasm as imp;
    } else {
        pub(crate) mod unsupported;
        pub(crate) use self::unsupported as imp;
    }
}
