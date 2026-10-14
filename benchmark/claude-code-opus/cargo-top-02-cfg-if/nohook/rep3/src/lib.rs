//! Cross-platform library.
//!
//! Platform-specific code lives in `src/sys/<platform>.rs`. Each backend
//! exposes the same set of items, and `sys/mod.rs` selects exactly one of
//! them with `cfg_if!`, so the rest of the crate never needs `#[cfg]`.

mod sys;

/// Returns a short, human-readable name for the platform this was built for.
pub fn platform_name() -> &'static str {
    sys::PLATFORM_NAME
}

/// Returns the platform's path-list separator (as used in `PATH`).
pub fn path_list_separator() -> char {
    sys::PATH_LIST_SEPARATOR
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_not_empty() {
        assert!(!platform_name().is_empty());
    }

    #[test]
    fn path_list_separator_matches_std() {
        let joined = std::env::join_paths(["a", "b"]).unwrap();
        let expected = format!("a{}b", path_list_separator());
        assert_eq!(joined.to_str().unwrap(), expected);
    }
}
