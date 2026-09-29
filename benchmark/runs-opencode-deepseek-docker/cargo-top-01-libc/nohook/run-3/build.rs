//! Compiles the native C shim that this tool links against.
//!
//! The `cc` crate locates a system C compiler through the usual `CC`/`AR`
//! environment variables (or a platform default such as `cc`/`clang`). It
//! emits the correct `cargo:rustc-link-*` directives for the target, so the
//! Rust side only has to declare the `extern "C"` signatures in `src/ffi.rs`.

fn main() {
    let include = "native";

    for source in ["native/sysinfo.c", "native/sysinfo.h"] {
        println!("cargo:rerun-if-changed={source}");
    }

    cc::Build::new()
        .file("native/sysinfo.c")
        .include(include)
        .flag_if_supported("-Wall")
        .flag_if_supported("-Wextra")
        .flag_if_supported("-Wconversion")
        .compile("systool_sysinfo");
}
