//! Platform-specific implementations.
//!
//! All dispatch happens here, in a single [`cfg_if!`] block. The rest of the
//! crate talks only to the flat re-exports below and never names a concrete
//! platform.

// `cfg_if!` is the right tool here: the branches select an *import* and a
// module, which an item-level `#[cfg]` cannot express without duplicating the
// surrounding `mod`/`pub use` around every arm.
cfg_if::cfg_if! {
    if #[cfg(platform_windows)] {
        #[path = "windows.rs"]
        mod imp;
    } else if #[cfg(platform_unix)] {
        #[path = "unix.rs"]
        mod imp;
    } else if #[cfg(platform_wasm)] {
        #[path = "wasm.rs"]
        mod imp;
    } else {
        #[path = "unsupported.rs"]
        mod imp;
    }
}

pub use imp::{sleep, uptime_millis};
