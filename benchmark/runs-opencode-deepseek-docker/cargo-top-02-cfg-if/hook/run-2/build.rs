//! Build script.
//!
//! It only exists to declare the custom `docsrs` cfg. Declaring it with
//! `rustc-check-cfg` keeps `unexpected_cfgs` warnings quiet, and gating it on
//! the `DOCS_RS` environment variable is the standard way to enable
//! nightly-only `doc(cfg(...))` annotations when the crate is built on
//! docs.rs.

fn main() {
    println!("cargo::rerun-if-changed=build.rs");
    println!("cargo::rustc-check-cfg=cfg(docsrs)");

    if std::env::var_os("DOCS_RS").is_some() {
        println!("cargo::rustc-cfg=docsrs");
    }
}
