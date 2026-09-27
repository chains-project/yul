fn main() {
    println!("cargo:rerun-if-changed=csrc/shim.c");
    println!("cargo:rerun-if-changed=csrc/shim.h");

    cc::Build::new()
        .file("csrc/shim.c")
        .include("csrc")
        .warnings(true)
        .compile("sysffi_shim");
}
