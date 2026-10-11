//! Integration tests asserting the public API behaves consistently per family.

use platform_kit::{Family, Platform, current};

#[test]
fn path_separator_matches_family() {
    match current().family {
        Family::Windows => assert_eq!(current().path_separator, '\\'),
        Family::Unix | Family::Wasm | Family::Other => {
            assert_eq!(current().path_separator, '/');
        }
        _ => {}
    }
}

#[test]
fn os_name_is_populated() {
    assert!(!current().os.is_empty());
}

#[test]
fn line_ending_is_known() {
    let ending = current().line_ending;
    assert!(ending == "\n" || ending == "\r\n", "unexpected {ending:?}");
}

#[test]
fn current_is_usable_in_const_contexts() {
    const PLATFORM: Platform = current();
    assert_eq!(PLATFORM.family, current().family);
}
