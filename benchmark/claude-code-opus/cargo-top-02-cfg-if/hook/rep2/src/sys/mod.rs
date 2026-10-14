//! Platform backends.
//!
//! Exactly one backend is compiled, selected below. Every backend must
//! define the same items with identical signatures:
//!
//! * `FAMILY: crate::Family`
//! * `LINE_ENDING: &str`
//! * `PATH_LIST_SEPARATOR: char`
//!
//! To add a platform: create `src/sys/<name>.rs` implementing the items
//! above, then add an arm to the `cfg_select!` before the `_` fallback.

cfg_select! {
    unix => {
        mod unix;
        pub use unix::*;
    }
    windows => {
        mod windows;
        pub use windows::*;
    }
    target_family = "wasm" => {
        mod wasm;
        pub use wasm::*;
    }
    _ => {
        mod fallback;
        pub use fallback::*;
    }
}
