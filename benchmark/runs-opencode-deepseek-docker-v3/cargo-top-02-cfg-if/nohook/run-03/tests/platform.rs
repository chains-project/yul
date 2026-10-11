//! Integration tests for the public `platform_kit` API.

use platform_kit::{
    arch, exe_suffix, line_ending, os, path_list_separator, path_separator, shared_library_prefix,
    shared_library_suffix,
};

#[test]
fn separators_match_the_detected_os() {
    let sep = path_separator();
    let list_sep = path_list_separator();

    if os().is_windows() {
        assert_eq!(sep, '\\');
        assert_eq!(list_sep, ';');
        assert_eq!(exe_suffix(), ".exe");
        assert_eq!(line_ending(), "\r\n");
    } else {
        assert_eq!(sep, '/');
        assert_eq!(list_sep, ':');
        assert_eq!(line_ending(), "\n");
    }
}

#[test]
fn shared_library_name_is_well_formed() {
    let name = format!(
        "{}platform_kit{}",
        shared_library_prefix(),
        shared_library_suffix()
    );
    assert!(name.contains("platform_kit"));
    assert!(shared_library_suffix().starts_with('.'));
}

#[test]
fn architecture_is_reported() {
    let arch = arch();
    assert!(!format!("{arch:?}").is_empty());
}
