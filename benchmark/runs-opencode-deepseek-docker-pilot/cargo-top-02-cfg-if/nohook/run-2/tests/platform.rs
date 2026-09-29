//! Integration tests that pin down the public, target-independent behavior.

use crossplat::{self, Endianness, Family};

#[test]
fn reports_a_platform_name() {
    assert!(!crossplat::name().is_empty());
}

#[test]
fn name_and_family_agree() {
    match crossplat::family() {
        Family::Unix => assert!(matches!(crossplat::name(), "linux" | "macos")),
        Family::Windows => assert_eq!(crossplat::name(), "windows"),
        Family::Wasm => assert_eq!(crossplat::name(), "wasm"),
        Family::Other => {}
        _ => {}
    }
}

#[test]
fn path_separator_is_platform_appropriate() {
    assert!(matches!(crossplat::path_separator(), '/' | '\\'));
}

#[test]
fn join_paths_inserts_separator() {
    let sep = crossplat::path_separator();
    assert_eq!(crossplat::join_paths("a", "b"), format!("a{sep}b"));
}

#[test]
fn join_paths_does_not_double_separator() {
    let sep = crossplat::path_separator();
    let a = format!("a{sep}");
    assert_eq!(crossplat::join_paths(&a, "b"), format!("a{sep}b"));
}

#[test]
fn line_ending_is_valid() {
    assert!(matches!(crossplat::line_ending(), "\n" | "\r\n"));
}

#[test]
fn pointer_width_matches_the_host() {
    assert!(matches!(crossplat::POINTER_WIDTH, 16 | 32 | 64));
    assert_eq!(
        crossplat::POINTER_WIDTH,
        (std::mem::size_of::<usize>() * 8) as u32
    );
}

#[test]
fn endianness_matches_the_host() {
    let expected = if cfg!(target_endian = "little") {
        Endianness::Little
    } else {
        Endianness::Big
    };
    assert_eq!(crossplat::endianness(), expected);
}

#[test]
fn host_specific_expectations() {
    if cfg!(target_os = "linux") {
        assert_eq!(crossplat::family(), Family::Unix);
        assert_eq!(crossplat::path_separator(), '/');
        assert_eq!(crossplat::line_ending(), "\n");
    }
}
