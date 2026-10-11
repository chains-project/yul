fn main() {
    println!("cargo:rerun-if-changed=src/native/shim.c");
    println!("cargo:rerun-if-changed=src/native/shim.h");

    cc::Build::new()
        .file("src/native/shim.c")
        .include("src/native")
        .warnings(true)
        .compile("shim");
}
