//! Cross-platform library skeleton.
//!
//! Platform-specific code lives in `src/sys/<platform>.rs`. Each backend
//! exposes the same set of items, and `sys/mod.rs` picks one with a single
//! `cfg_if!` chain, so the rest of the crate never needs `#[cfg]` attributes.

mod sys;

/// Returns a human-readable name for the platform this crate was compiled for.
pub fn platform_name() -> &'static str {
    sys::PLATFORM_NAME
}

/// Returns the platform's native path separator.
pub fn path_separator() -> char {
    sys::path_separator()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_not_empty() {
        assert!(!platform_name().is_empty());
    }

    #[test]
    fn path_separator_matches_std() {
        assert_eq!(path_separator(), std::path::MAIN_SEPARATOR);
    }
}
