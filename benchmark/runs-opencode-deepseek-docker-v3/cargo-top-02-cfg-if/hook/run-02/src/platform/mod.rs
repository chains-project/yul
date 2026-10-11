//! Platform selection.
//!
//! This module owns *all* of the crate's conditional compilation. Each branch
//! pulls in a small module that implements [`Platform`] for one target family,
//! then re-exports it as [`Current`]. Keeping the dispatch here means the rest
//! of the crate reads as ordinary, portable Rust.

use cfg_if::cfg_if;

cfg_if! {
    if #[cfg(target_arch = "wasm32")] {
        mod wasm;
        pub use wasm::Wasm as Current;
    } else if #[cfg(windows)] {
        mod windows;
        pub use windows::Windows as Current;
    } else if #[cfg(unix)] {
        mod unix;
        pub use unix::Unix as Current;
    } else {
        compile_error!(
            "crossplat does not support this target yet. \
             Add a module under `src/platform/` and a branch to the `cfg_if!` \
             block in `src/platform/mod.rs`."
        );
    }
}

/// The behaviour every supported platform must provide.
///
/// Implement this trait in a per-platform module and add a matching branch to
/// the [`cfg_if!`] dispatch above. No other file needs to change.
pub trait Platform {
    /// A short, human-readable identifier for the platform.
    const NAME: &'static str;

    /// The memory page size, in bytes.
    fn page_size() -> usize;

    /// A reasonable upper bound on useful worker threads.
    fn max_threads() -> usize;
}
