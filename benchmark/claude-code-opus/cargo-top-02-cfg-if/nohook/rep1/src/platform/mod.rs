//! Compile-time backend selection.
//!
//! Each backend module must expose the same items:
//! - `const PLATFORM_NAME: &str`
//! - `fn path_separator() -> char`
//!
//! Branches are checked top to bottom; the first match wins, so put more
//! specific predicates (e.g. `target_os = "macos"`) before broader ones
//! (e.g. `unix`).

cfg_if::cfg_if! {
    if #[cfg(windows)] {
        mod windows;
        pub use self::windows::*;
    } else if #[cfg(any(target_os = "macos", target_os = "ios"))] {
        mod apple;
        pub use self::apple::*;
    } else if #[cfg(target_os = "linux")] {
        mod linux;
        pub use self::linux::*;
    } else if #[cfg(all(target_family = "wasm", target_os = "unknown"))] {
        mod wasm;
        pub use self::wasm::*;
    } else if #[cfg(unix)] {
        mod unix;
        pub use self::unix::*;
    } else {
        compile_error!("platform_lib: unsupported target platform");
    }
}
