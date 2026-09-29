use std::env;

fn main() {
    let target_os = env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();

    // Link against the platform C math library. On Unix this is a distinct
    // native library (`libm`); on Windows the math symbols live in the CRT.
    if target_os != "windows" {
        println!("cargo:rustc-link-lib=m");
    }

    // Linking a bundled native library looks like this:
    //
    // ```ignore
    // let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    // println!("cargo:rustc-link-search=native={manifest_dir}/native/lib");
    // println!("cargo:rustc-link-lib=static=myclib");
    // ```
    //
    // If you ship the C sources with the crate, add the `cc` crate as a
    // build-dependency and compile them here:
    //
    // ```ignore
    // cc::Build::new()
    //     .file("native/src/myclib.c")
    //     .include("native/include")
    //     .compile("myclib");
    // ```

    println!("cargo:rerun-if-changed=build.rs");
}
