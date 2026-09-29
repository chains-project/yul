//! Integration tests exercise the crate exactly as a downstream user would,
//! which also proves the public `cfg` aliases survive across crate boundaries.

use crossplat::{paths, platform, Platform};

#[test]
fn detected_platform_is_consistent_across_the_public_api() {
    let here = Platform::current();

    assert_eq!(here, Platform::current());
    assert_eq!(here.name(), here.name());
    assert_eq!(platform::is_desktop_build(), here.is_desktop());
    assert_eq!(platform::is_mobile_build(), here.is_mobile());
}

#[test]
fn path_conventions_are_internally_consistent() {
    let separator = paths::separator();
    let env_separator = paths::env_separator();

    assert!(separator == '/' || separator == '\\');
    assert!(env_separator == ':' || env_separator == ';');
    assert!(!paths::dynamic_library_extension().is_empty());
}
