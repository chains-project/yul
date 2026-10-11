fn main() {
    println!("cargo:rerun-if-changed=csrc/helper.c");
    println!("cargo:rerun-if-changed=csrc/helper.h");

    cc::Build::new()
        .file("csrc/helper.c")
        .include("csrc")
        .warnings(true)
        .compile("helper");
}
