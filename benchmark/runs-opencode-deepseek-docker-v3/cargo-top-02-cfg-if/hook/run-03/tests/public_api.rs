use crossplat::{Family, Platform, current_family, current_platform, path_separator};

#[test]
fn public_api_is_usable_without_cfg_gates() {
    // Consumers can query the platform at runtime instead of writing their own
    // `#[cfg]` blocks.
    let platform: Platform = current_platform();
    let family: Family = current_family();

    assert_eq!(platform.name(), platform.name());
    assert!(!family.name().is_empty());
    assert!(matches!(path_separator(), '/' | '\\'));
}

#[test]
fn downstream_can_still_use_plain_cfg_where_needed() {
    #[cfg(windows)]
    assert_eq!(current_platform(), Platform::Windows);

    #[cfg(unix)]
    assert_eq!(current_family(), Family::Unix);
}
