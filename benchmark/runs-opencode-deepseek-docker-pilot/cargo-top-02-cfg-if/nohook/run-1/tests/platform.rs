//! Integration tests.
//!
//! Note that build-script `cfg` aliases (e.g. `unix_family`) are applied to
//! integration tests as well, so the tests read the same way as the crate.

use xplat::platform::{platform, PATH_SEPARATOR};
use xplat::Family;

#[test]
fn reports_a_known_family() {
    let info = platform();
    assert!(!info.name.is_empty());
    assert!(matches!(
        info.family,
        Family::Unix | Family::Windows | Family::Wasm | Family::Other
    ));
}

#[cfg(unix_family)]
#[test]
fn unix_family_selects_unix_backend() {
    assert_eq!(platform().family, Family::Unix);
    assert_eq!(platform().name, "unix");
    assert_eq!(PATH_SEPARATOR, '/');
}

#[cfg(windows_family)]
#[test]
fn windows_family_selects_windows_backend() {
    assert_eq!(platform().family, Family::Windows);
    assert_eq!(platform().name, "windows");
    assert_eq!(PATH_SEPARATOR, '\\');
}

#[cfg(has_page_size)]
#[test]
fn page_size_is_available_and_sane() {
    let size = xplat::platform::page_size();
    assert!(size >= 4096, "unexpected page size: {size}");
    assert!(size.is_power_of_two(), "unexpected page size: {size}");
}
