fn main() {
    println!("cargo:rerun-if-changed=csrc/checksum.c");

    cc::Build::new()
        .file("csrc/checksum.c")
        .warnings(true)
        .compile("checksum");
}
