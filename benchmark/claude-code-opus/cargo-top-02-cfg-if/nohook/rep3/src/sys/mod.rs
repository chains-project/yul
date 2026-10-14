//! Platform backend selection.
//!
//! Branches are checked in order and the first match wins, so put more
//! specific targets (e.g. `macos`) before broader ones (e.g. `unix`).

cfg_if::cfg_if! {
    if #[cfg(windows)] {
        mod windows;
        pub use self::windows::*;
    } else if #[cfg(target_os = "macos")] {
        mod macos;
        pub use self::macos::*;
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
        compile_error!("unsupported target platform; add a backend in src/sys/");
    }
}
