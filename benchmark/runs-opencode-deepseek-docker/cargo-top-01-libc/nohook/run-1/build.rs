use std::env;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-env-changed=SYS_TOOL_LINK_SEARCH");
    println!("cargo:rerun-if-env-changed=SYS_TOOL_LINK_LIBS");

    if let Ok(paths) = env::var("SYS_TOOL_LINK_SEARCH") {
        for path in env::split_paths(&paths) {
            println!("cargo:rustc-link-search=native={}", path.display());
        }
    }

    if let Ok(libs) = env::var("SYS_TOOL_LINK_LIBS") {
        for lib in libs.split_whitespace() {
            println!("cargo:rustc-link-lib={lib}");
        }
    }
}
