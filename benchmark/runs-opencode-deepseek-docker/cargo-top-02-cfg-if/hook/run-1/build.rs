//! Declares project-wide `cfg` aliases so platform checks read cleanly.
//!
//! Raw predicates such as `#[cfg(target_os = "macos")]` are noisy and easy to
//! mistype once a crate grows past one or two targets. Instead of repeating
//! them at every use site, they are defined exactly once here and expanded to
//! short aliases like `#[cfg(macos)]`.
//!
//! `cfg_aliases!` also emits `cargo:rustc-check-cfg`, so the `unexpected_cfgs`
//! lint understands these names and will still catch genuine typos.

use cfg_aliases::cfg_aliases;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    cfg_aliases! {
        // Operating-system families.
        macos:   { target_os = "macos" },
        linux:   { target_os = "linux" },
        android: { target_os = "android" },
        ios:     { target_os = "ios" },

        // WebAssembly targets.
        wasm: { target_arch = "wasm32" },

        // Capability groups, built from the families above.
        desktop: { any(windows, macos, linux) },
        mobile:  { any(android, ios) },
        has_threads: { any(windows, macos, linux, android, target_os = "freebsd") },

        // Pointer widths.
        ptr_64: { target_pointer_width = "64" },
        ptr_32: { target_pointer_width = "32" },
    }
}
