//! Turns long target predicates into short, readable `cfg` aliases.
//!
//! Keeping these definitions in one place means the rest of the crate can use
//! names such as `platform_windows` instead of repeating
//! `#[cfg(all(target_os = "windows", ...))]` on every item.
//!
//! Note: do not add a trailing comma inside `any(...)` / `all(...)`; the
//! `cfg_aliases` parser does not accept it and expands without bound.

use cfg_aliases::cfg_aliases;

fn main() {
    cfg_aliases! {
        // Operating-system aliases.
        platform_windows: { target_os = "windows" },
        platform_linux:   { target_os = "linux" },
        platform_apple:   { any(target_os = "macos", target_os = "ios", target_os = "tvos", target_os = "watchos") },
        platform_bsd:     { any(target_os = "freebsd", target_os = "openbsd", target_os = "netbsd", target_os = "dragonfly") },

        // Target-family alias. `wasm` spans several `target_os` values
        // (`unknown`, `wasi`, ...), so it is described by family instead.
        platform_wasm: { target_family = "wasm" },

        // Architecture alias.
        pointer_64: { target_pointer_width = "64" },
    }
}
