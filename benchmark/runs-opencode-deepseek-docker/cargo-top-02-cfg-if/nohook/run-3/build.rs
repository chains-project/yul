//! Declares the semantic `cfg` aliases used throughout the crate.
//!
//! Raw `target_*` predicates are mapped to short, intention-revealing names
//! exactly once here, so call sites read as `#[cfg(platform_unix)]` rather
//! than `#[cfg(all(target_family = "unix", not(target_os = "redox")))]`.
//!
//! Cargo exposes the target being compiled for to the build script through
//! `CARGO_CFG_TARGET_*`, which is what makes this correct when
//! cross-compiling (the build script itself runs on the host).

use std::env;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    let family = env::var("CARGO_CFG_TARGET_FAMILY").unwrap_or_default();
    let families: Vec<&str> = family.split(',').filter(|s| !s.is_empty()).collect();

    let arch = env::var("CARGO_CFG_TARGET_ARCH").unwrap_or_default();
    let pointer_width = env::var("CARGO_CFG_TARGET_POINTER_WIDTH").unwrap_or_default();

    let aliases = [
        ("platform_windows", families.contains(&"windows")),
        ("platform_unix", families.contains(&"unix")),
        ("platform_wasm", families.contains(&"wasm")),
        ("arch_x86", arch == "x86"),
        ("arch_x86_64", arch == "x86_64"),
        ("arch_aarch64", arch == "aarch64"),
        ("pointer_64", pointer_width == "64"),
        ("pointer_32", pointer_width == "32"),
    ];

    for (name, enabled) in aliases {
        // Teach rustc about the alias so `unexpected_cfgs` stays quiet.
        println!("cargo:rustc-check-cfg=cfg({name})");
        if enabled {
            println!("cargo:rustc-cfg={name}");
        }
    }
}
