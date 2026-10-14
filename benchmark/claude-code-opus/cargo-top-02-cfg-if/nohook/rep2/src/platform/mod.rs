//! Compile-time selection of the platform backend.
//!
//! Each backend module must export the same set of items. `cfg_select!` uses
//! the first arm that matches, so put more specific predicates first.

cfg_select! {
    windows => {
        mod windows;
        pub use windows::*;
    }
    unix => {
        mod unix;
        pub use unix::*;
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
