//! Cross-platform library skeleton.
//!
//! Platform-specific code lives in `src/platform/`, one file per target
//! family. [`cfg_if::cfg_if!`] selects exactly one backend at compile time,
//! so the rest of the crate only ever sees a single, uniform API.

mod platform;

pub use platform::PLATFORM_NAME;

/// Returns a human-readable name for the platform this crate was built for.
pub fn platform_name() -> &'static str {
    PLATFORM_NAME
}

/// Returns the platform's native path separator.
pub fn path_separator() -> char {
    platform::path_separator()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_not_empty() {
        assert!(!platform_name().is_empty());
    }

    #[test]
    fn separator_matches_std() {
        assert_eq!(path_separator(), std::path::MAIN_SEPARATOR);
    }
}
