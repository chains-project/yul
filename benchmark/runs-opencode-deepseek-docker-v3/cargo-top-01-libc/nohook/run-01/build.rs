fn main() {
    println!("cargo:rerun-if-changed=csrc/syshelper.c");

    cc::Build::new()
        .file("csrc/syshelper.c")
        .warnings(true)
        .opt_level(2)
        .compile("syshelper");

    println!("cargo:rustc-link-lib=static=syshelper");
}
