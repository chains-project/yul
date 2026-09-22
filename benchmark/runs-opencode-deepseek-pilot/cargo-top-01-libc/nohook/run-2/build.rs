fn main() {
    println!("cargo:rerun-if-changed=csrc/native.c");

    cc::Build::new()
        .file("csrc/native.c")
        .warnings(true)
        .compile("native");
}
