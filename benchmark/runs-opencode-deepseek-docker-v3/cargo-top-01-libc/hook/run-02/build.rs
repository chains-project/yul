fn main() {
    println!("cargo:rerun-if-changed=native/device.c");
    println!("cargo:rerun-if-changed=native/include/device.h");

    cc::Build::new()
        .file("native/device.c")
        .include("native/include")
        .warnings(true)
        .extra_warnings(true)
        .compile("systool_device");
}
