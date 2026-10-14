//! Cross-platform library.
//!
//! Platform-specific code lives in [`platform`], which picks one backend at
//! compile time. Everything else should go through the API exported here and
//! stay free of `#[cfg]` attributes.

mod platform;

pub use platform::{family, path_separator};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn family_is_known() {
        assert!(["unix", "windows", "wasm", "unknown"].contains(&family()));
    }

    #[test]
    fn separator_matches_std() {
        assert_eq!(path_separator(), std::path::MAIN_SEPARATOR);
    }
}
