//! Platform backends.
//!
//! Each backend exposes the same set of items; exactly one is compiled in and
//! re-exported here. Adding a platform means adding one file and one branch.

cfg_if::cfg_if! {
    if #[cfg(unix_backend)] {
        mod unix;
        pub use unix::*;
    } else if #[cfg(windows_backend)] {
        mod windows;
        pub use windows::*;
    } else if #[cfg(wasm_backend)] {
        mod wasm;
        pub use wasm::*;
    } else {
        mod fallback;
        pub use fallback::*;
    }
}
