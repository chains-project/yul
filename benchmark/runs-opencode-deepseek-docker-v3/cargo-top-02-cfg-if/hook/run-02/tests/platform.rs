//! Integration tests for the platform-independent public API.

use crossplat::{Current, Platform};

fn assert_platform<P: Platform>() {}

#[test]
fn current_implements_platform() {
    assert_platform::<Current>();
}

#[test]
fn metadata_is_sane() {
    assert_ne!(crossplat::name(), "");
    assert!(crossplat::page_size().is_power_of_two());
    assert!(crossplat::max_threads() >= 1);
}
