//! Platform backend selection.
//!
//! Branches are checked in order and the first match wins, so put more
//! specific targets (e.g. `macos`) before broader ones (e.g. `unix`).
//! Every backend has to export the same items.

cfg_if::cfg_if! {
    if #[cfg(windows)] {
        mod windows;
        pub(crate) use windows::*;
    } else if #[cfg(any(target_os = "macos", target_os = "ios"))] {
        mod apple;
        pub(crate) use apple::*;
    } else if #[cfg(target_os = "linux")] {
        mod linux;
        pub(crate) use linux::*;
    } else if #[cfg(all(target_family = "wasm", target_os = "unknown"))] {
        mod wasm;
        pub(crate) use wasm::*;
    } else if #[cfg(unix)] {
        mod unix;
        pub(crate) use unix::*;
    } else {
        mod unsupported;
        pub(crate) use unsupported::*;
    }
}
