//! Defines short, named `cfg` aliases so platform checks read as intent
//! (`#[cfg(apple)]`) rather than as long `any(...)`/`all(...)` expressions.
//!
//! `cfg_aliases` also emits the matching `cargo::rustc-check-cfg` lines, so
//! misspelled aliases are still caught by the `unexpected_cfgs` lint.

use cfg_aliases::cfg_aliases;

fn main() {
    cfg_aliases! {
        // Operating-system groups
        apple: { any(target_os = "macos", target_os = "ios", target_os = "tvos", target_os = "watchos", target_os = "visionos") },
        linux_like: { any(target_os = "linux", target_os = "android") },
        bsd: { any(target_os = "freebsd", target_os = "openbsd", target_os = "netbsd", target_os = "dragonfly") },

        // Backend selection — exactly one of these is active for any target.
        unix_backend: { all(unix, not(target_family = "wasm")) },
        windows_backend: { windows },
        wasm_backend: { target_family = "wasm" },
        fallback_backend: { not(any(unix_backend, windows_backend, wasm_backend)) },
    }
}
