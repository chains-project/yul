fn main() {
    cc::Build::new()
        .file("src/native/example.c")
        .warnings(true)
        .compile("example");

    println!("cargo:rerun-if-changed=src/native/example.c");
}
