//! Verifies that the build-script aliases agree with the compiled platform.

use multiplatform::{PLATFORM, Platform, line_ending, path_separator};

/// The platform implied by the active cfg alias.
fn platform_from_aliases() -> Platform {
    if cfg!(platform_unix) {
        Platform::Unix
    } else if cfg!(platform_windows) {
        Platform::Windows
    } else if cfg!(platform_wasm) {
        Platform::Wasm
    } else {
        Platform::Other
    }
}

#[test]
fn exactly_one_alias_is_active() {
    let active = [
        cfg!(platform_unix),
        cfg!(platform_windows),
        cfg!(platform_wasm),
        cfg!(platform_other),
    ]
    .into_iter()
    .filter(|&on| on)
    .count();

    assert_eq!(active, 1, "expected exactly one platform alias");
}

#[test]
fn reported_platform_matches_the_alias() {
    assert_eq!(PLATFORM, platform_from_aliases());
}

#[test]
fn conventions_match_the_platform() {
    let (separator, ending) = match PLATFORM {
        Platform::Windows => ('\\', "\r\n"),
        Platform::Unix | Platform::Wasm | Platform::Other => ('/', "\n"),
        _ => unreachable!("Platform is #[non_exhaustive]"),
    };

    assert_eq!(path_separator(), separator);
    assert_eq!(line_ending(), ending);
}

#[test]
fn platform_name_is_stable() {
    assert_eq!(
        PLATFORM.name(),
        match PLATFORM {
            Platform::Unix => "unix",
            Platform::Windows => "windows",
            Platform::Wasm => "wasm",
            Platform::Other => "other",
            _ => unreachable!("Platform is #[non_exhaustive]"),
        }
    );
}
