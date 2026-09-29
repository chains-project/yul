use std::env;

fn main() {
    let target = env::var("TARGET").unwrap_or_default();

    let mut build = cc::Build::new();
    build
        .file("csrc/native.c")
        .include("csrc")
        .warnings(true)
        .extra_warnings(true)
        .opt_level(2);

    if target.contains("msvc") {
        build.flag_if_supported("/W4");
    }

    build.compile("sysnative");

    println!("cargo:rerun-if-changed=csrc/native.c");
    println!("cargo:rerun-if-changed=csrc/native.h");
}
