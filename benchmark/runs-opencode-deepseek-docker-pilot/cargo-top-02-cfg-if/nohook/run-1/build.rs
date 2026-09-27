#![recursion_limit = "256"]

//! Central declaration of every conditional-compilation alias used by the
//! crate.
//!
//! Keeping the raw `target_*` predicates here — and only here — lets the rest
//! of the codebase read in terms of *intent*:
//!
//! ```ignore
//! #[cfg(unix_family)]
//! fn something() { /* ... */ }
//! ```
//!
//! instead of long, error-prone chains such as
//! `any(target_os = "linux", target_os = "macos", ...)`.
//!
//! To add a platform, add/extend an alias here and add a backend under
//! `src/platform/`. Nothing else should need to change.

use cfg_aliases::cfg_aliases;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    cfg_aliases! {
        // ---- Operating-system families --------------------------------
        unix_family:    { any(target_family = "unix") },
        windows_family: { target_family = "windows" },
        wasm_family:    { target_family = "wasm" },

        // ---- Coarse target classes ------------------------------------
        // NOTE: cfg_aliases' parser rejects a trailing comma inside a nested
        // list such as `any(a, b,)` (it surfaces as a bogus recursion-limit
        // error), so keep these comma lists tight.
        desktop: { any(target_os = "linux", target_os = "macos", target_os = "windows") },
        mobile: { any(target_os = "android", target_os = "ios") },

        // ---- Architecture ---------------------------------------------
        arch_64: { target_pointer_width = "64" },

        // ---- Capabilities ---------------------------------------------
        // Predicates are inlined rather than referencing other aliases:
        // cfg_aliases expands aliases eagerly, and cross-references blow up
        // the macro recursion limit.
        has_std:        { feature = "std" },
        has_threads:    { all(feature = "std", not(target_family = "wasm")) },
        has_atomic_ptr: { all(feature = "std", target_has_atomic = "ptr") },
        has_page_size:  { any(target_family = "unix", target_family = "windows") },
    }
}
